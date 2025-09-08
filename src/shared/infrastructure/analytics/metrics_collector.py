"""
Performance Metrics Collector

Real-time metrics collection system for the RAG Interface.
Collects, aggregates, and analyzes performance data across all services.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int
    sum: float
    min: float
    max: float
    mean: float
    median: float
    p95: float
    p99: float
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Real-time metrics collection and analysis system.
    
    Collects performance metrics from all services and provides
    real-time analytics and alerting capabilities.
    """

    def __init__(
        self,
        retention_period: timedelta = timedelta(hours=24),
        aggregation_interval: int = 60,  # seconds
        max_metrics_per_type: int = 10000
    ):
        """
        Initialize metrics collector.
        
        Args:
            retention_period: How long to keep metrics
            aggregation_interval: Interval for metric aggregation
            max_metrics_per_type: Maximum metrics to keep per type
        """
        self.retention_period = retention_period
        self.aggregation_interval = aggregation_interval
        self.max_metrics_per_type = max_metrics_per_type
        
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.max_metrics_per_type))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        
        # Aggregated data
        self.aggregated_metrics: Dict[str, List[MetricSummary]] = defaultdict(list)
        
        # Event handlers
        self.alert_handlers: List[Callable] = []
        self.threshold_rules: Dict[str, Dict[str, Any]] = {}
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.aggregation_task: Optional[asyncio.Task] = None
        
        logger.info("Initialized metrics collector")

    async def start(self):
        """Start background tasks for metrics processing."""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if not self.aggregation_task:
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
        
        logger.info("Started metrics collector background tasks")

    async def stop(self):
        """Stop background tasks."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.aggregation_task:
            self.aggregation_task.cancel()
            try:
                await self.aggregation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped metrics collector background tasks")

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a counter metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metadata=metadata or {}
        )
        
        self._store_metric(metric)
        self.counters[name] += value

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a gauge metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metadata=metadata or {}
        )
        
        self._store_metric(metric)
        self.gauges[name] = value

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a histogram metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metadata=metadata or {}
        )
        
        self._store_metric(metric)

    def record_timer(
        self,
        name: str,
        duration: float,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a timer metric (duration in seconds)."""
        metric = Metric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metadata=metadata or {}
        )
        
        self._store_metric(metric)

    def timer(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, labels)

    def _store_metric(self, metric: Metric):
        """Store metric and check thresholds."""
        self.metrics[metric.name].append(metric)
        
        # Check threshold rules
        self._check_thresholds(metric)

    def _check_thresholds(self, metric: Metric):
        """Check if metric violates any threshold rules."""
        if metric.name in self.threshold_rules:
            rule = self.threshold_rules[metric.name]
            
            # Check threshold
            if "max_value" in rule and metric.value > rule["max_value"]:
                self._trigger_alert(metric, f"Value {metric.value} exceeds maximum {rule['max_value']}")
            
            if "min_value" in rule and metric.value < rule["min_value"]:
                self._trigger_alert(metric, f"Value {metric.value} below minimum {rule['min_value']}")

    def _trigger_alert(self, metric: Metric, message: str):
        """Trigger alert for metric threshold violation."""
        alert_data = {
            "metric": metric.name,
            "value": metric.value,
            "timestamp": metric.timestamp.isoformat(),
            "message": message,
            "labels": metric.labels
        }
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(alert_data))
                else:
                    handler(alert_data)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def add_threshold_rule(
        self,
        metric_name: str,
        max_value: Optional[float] = None,
        min_value: Optional[float] = None,
        **kwargs
    ):
        """Add threshold rule for a metric."""
        rule = {}
        if max_value is not None:
            rule["max_value"] = max_value
        if min_value is not None:
            rule["min_value"] = min_value
        rule.update(kwargs)
        
        self.threshold_rules[metric_name] = rule
        logger.info(f"Added threshold rule for {metric_name}: {rule}")

    def add_alert_handler(self, handler: Callable):
        """Add alert handler function."""
        self.alert_handlers.append(handler)

    def get_metric_summary(
        self,
        metric_name: str,
        time_range: Optional[timedelta] = None
    ) -> Optional[MetricSummary]:
        """Get summary statistics for a metric."""
        if metric_name not in self.metrics:
            return None
        
        # Filter by time range
        cutoff_time = datetime.utcnow() - (time_range or timedelta(hours=1))
        filtered_metrics = [
            m for m in self.metrics[metric_name]
            if m.timestamp >= cutoff_time
        ]
        
        if not filtered_metrics:
            return None
        
        values = [m.value for m in filtered_metrics]
        
        return MetricSummary(
            name=metric_name,
            count=len(values),
            sum=sum(values),
            min=min(values),
            max=max(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            p95=self._percentile(values, 95),
            p99=self._percentile(values, 99)
        )

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "metric_counts": {name: len(metrics) for name, metrics in self.metrics.items()},
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_metrics_by_type(self, metric_type: MetricType) -> Dict[str, List[Metric]]:
        """Get metrics filtered by type."""
        filtered = {}
        for name, metrics in self.metrics.items():
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if type_metrics:
                filtered[name] = type_metrics
        return filtered

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    async def _cleanup_loop(self):
        """Background task to clean up old metrics."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics cleanup failed: {e}")

    async def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = datetime.utcnow() - self.retention_period
        
        for name, metrics in self.metrics.items():
            # Remove old metrics
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()

    async def _aggregation_loop(self):
        """Background task to aggregate metrics."""
        while True:
            try:
                await asyncio.sleep(self.aggregation_interval)
                await self._aggregate_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics aggregation failed: {e}")

    async def _aggregate_metrics(self):
        """Aggregate metrics for the current interval."""
        current_time = datetime.utcnow()
        
        for name, metrics in self.metrics.items():
            if not metrics:
                continue
            
            # Get metrics from the last aggregation interval
            cutoff_time = current_time - timedelta(seconds=self.aggregation_interval)
            interval_metrics = [
                m for m in metrics
                if m.timestamp >= cutoff_time
            ]
            
            if interval_metrics:
                values = [m.value for m in interval_metrics]
                summary = MetricSummary(
                    name=name,
                    count=len(values),
                    sum=sum(values),
                    min=min(values),
                    max=max(values),
                    mean=statistics.mean(values),
                    median=statistics.median(values),
                    p95=self._percentile(values, 95),
                    p99=self._percentile(values, 99)
                )
                
                self.aggregated_metrics[name].append(summary)
                
                # Keep only recent aggregations
                max_aggregations = int(self.retention_period.total_seconds() / self.aggregation_interval)
                if len(self.aggregated_metrics[name]) > max_aggregations:
                    self.aggregated_metrics[name] = self.aggregated_metrics[name][-max_aggregations:]


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_timer(self.name, duration, self.labels)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Convenience functions
def record_counter(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
    """Record a counter metric."""
    get_metrics_collector().record_counter(name, value, labels)


def record_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Record a gauge metric."""
    get_metrics_collector().record_gauge(name, value, labels)


def record_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Record a histogram metric."""
    get_metrics_collector().record_histogram(name, value, labels)


def timer(name: str, labels: Optional[Dict[str, str]] = None):
    """Context manager for timing operations."""
    return get_metrics_collector().timer(name, labels)


async def start_metrics_collection():
    """Start the global metrics collector."""
    collector = get_metrics_collector()
    await collector.start()


async def stop_metrics_collection():
    """Stop the global metrics collector."""
    collector = get_metrics_collector()
    await collector.stop()
