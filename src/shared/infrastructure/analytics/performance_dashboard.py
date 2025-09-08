"""
Performance Dashboard

Real-time performance dashboard for the RAG Interface system.
Provides web-based visualization of metrics and system health.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .metrics_collector import MetricsCollector, get_metrics_collector

logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """
    Real-time performance dashboard with WebSocket updates.
    
    Provides a web interface for monitoring system performance,
    viewing metrics, and analyzing trends.
    """

    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        update_interval: int = 5  # seconds
    ):
        """
        Initialize performance dashboard.
        
        Args:
            metrics_collector: Metrics collector instance
            update_interval: How often to send updates to clients
        """
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.update_interval = update_interval
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Dashboard data cache
        self.dashboard_data: Dict[str, Any] = {}
        
        # Background task
        self.update_task: Optional[asyncio.Task] = None
        
        logger.info("Initialized performance dashboard")

    def create_app(self) -> FastAPI:
        """Create FastAPI application for the dashboard."""
        app = FastAPI(title="RAG Interface Performance Dashboard")
        
        # Add routes
        app.add_api_route("/", self.dashboard_page, methods=["GET"])
        app.add_api_route("/api/metrics", self.get_metrics_api, methods=["GET"])
        app.add_api_route("/api/health", self.get_health_api, methods=["GET"])
        app.add_websocket("/ws", self.websocket_endpoint)
        
        return app

    async def dashboard_page(self, request: Request) -> HTMLResponse:
        """Serve the main dashboard page."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG Interface Performance Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }
                .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
                .metric-unit { font-size: 14px; color: #666; }
                .chart-container { height: 300px; margin-top: 15px; }
                .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
                .status-healthy { background-color: #28a745; }
                .status-warning { background-color: #ffc107; }
                .status-error { background-color: #dc3545; }
                .timestamp { text-align: center; color: #666; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>RAG Interface Performance Dashboard</h1>
                    <div id="connection-status">
                        <span class="status-indicator status-error"></span>
                        <span>Connecting...</span>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Request Rate</div>
                        <div class="metric-value" id="request-rate">0</div>
                        <div class="metric-unit">requests/sec</div>
                        <div class="chart-container">
                            <canvas id="request-rate-chart"></canvas>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Response Time</div>
                        <div class="metric-value" id="response-time">0</div>
                        <div class="metric-unit">ms</div>
                        <div class="chart-container">
                            <canvas id="response-time-chart"></canvas>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Error Rate</div>
                        <div class="metric-value" id="error-rate">0</div>
                        <div class="metric-unit">%</div>
                        <div class="chart-container">
                            <canvas id="error-rate-chart"></canvas>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Active Connections</div>
                        <div class="metric-value" id="active-connections">0</div>
                        <div class="metric-unit">connections</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Memory Usage</div>
                        <div class="metric-value" id="memory-usage">0</div>
                        <div class="metric-unit">MB</div>
                        <div class="chart-container">
                            <canvas id="memory-chart"></canvas>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">CPU Usage</div>
                        <div class="metric-value" id="cpu-usage">0</div>
                        <div class="metric-unit">%</div>
                        <div class="chart-container">
                            <canvas id="cpu-chart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="timestamp" id="last-update">
                    Last updated: Never
                </div>
            </div>

            <script>
                // WebSocket connection
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                const connectionStatus = document.getElementById('connection-status');
                
                // Chart configurations
                const chartConfig = {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { display: false },
                            y: { beginAtZero: true }
                        }
                    }
                };
                
                // Initialize charts
                const charts = {
                    requestRate: new Chart(document.getElementById('request-rate-chart'), JSON.parse(JSON.stringify(chartConfig))),
                    responseTime: new Chart(document.getElementById('response-time-chart'), JSON.parse(JSON.stringify(chartConfig))),
                    errorRate: new Chart(document.getElementById('error-rate-chart'), JSON.parse(JSON.stringify(chartConfig))),
                    memory: new Chart(document.getElementById('memory-chart'), JSON.parse(JSON.stringify(chartConfig))),
                    cpu: new Chart(document.getElementById('cpu-chart'), JSON.parse(JSON.stringify(chartConfig)))
                };
                
                ws.onopen = function(event) {
                    connectionStatus.innerHTML = '<span class="status-indicator status-healthy"></span><span>Connected</span>';
                };
                
                ws.onclose = function(event) {
                    connectionStatus.innerHTML = '<span class="status-indicator status-error"></span><span>Disconnected</span>';
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                function updateDashboard(data) {
                    // Update metric values
                    document.getElementById('request-rate').textContent = data.request_rate || 0;
                    document.getElementById('response-time').textContent = Math.round(data.response_time || 0);
                    document.getElementById('error-rate').textContent = (data.error_rate || 0).toFixed(2);
                    document.getElementById('active-connections').textContent = data.active_connections || 0;
                    document.getElementById('memory-usage').textContent = Math.round(data.memory_usage || 0);
                    document.getElementById('cpu-usage').textContent = (data.cpu_usage || 0).toFixed(1);
                    
                    // Update charts
                    const timestamp = new Date().toLocaleTimeString();
                    updateChart(charts.requestRate, timestamp, data.request_rate || 0);
                    updateChart(charts.responseTime, timestamp, data.response_time || 0);
                    updateChart(charts.errorRate, timestamp, data.error_rate || 0);
                    updateChart(charts.memory, timestamp, data.memory_usage || 0);
                    updateChart(charts.cpu, timestamp, data.cpu_usage || 0);
                    
                    // Update timestamp
                    document.getElementById('last-update').textContent = `Last updated: ${new Date().toLocaleString()}`;
                }
                
                function updateChart(chart, label, value) {
                    chart.data.labels.push(label);
                    chart.data.datasets[0].data.push(value);
                    
                    // Keep only last 20 data points
                    if (chart.data.labels.length > 20) {
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                    }
                    
                    chart.update('none');
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    async def get_metrics_api(self) -> Dict[str, Any]:
        """API endpoint to get current metrics."""
        return await self._collect_dashboard_data()

    async def get_health_api(self) -> Dict[str, Any]:
        """API endpoint to get system health."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_connections": len(self.active_connections),
            "metrics_collector_running": self.update_task is not None
        }

    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            # Send initial data
            data = await self._collect_dashboard_data()
            await websocket.send_text(json.dumps(data))
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                # Client will receive updates from the broadcast task
                
        except WebSocketDisconnect:
            pass
        finally:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def start(self):
        """Start the dashboard update task."""
        if not self.update_task:
            self.update_task = asyncio.create_task(self._update_loop())
        logger.info("Started performance dashboard")

    async def stop(self):
        """Stop the dashboard update task."""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
            self.update_task = None
        logger.info("Stopped performance dashboard")

    async def _update_loop(self):
        """Background task to update dashboard data and broadcast to clients."""
        while True:
            try:
                # Collect latest data
                data = await self._collect_dashboard_data()
                self.dashboard_data = data
                
                # Broadcast to all connected clients
                if self.active_connections:
                    message = json.dumps(data)
                    disconnected = []
                    
                    for connection in self.active_connections:
                        try:
                            await connection.send_text(message)
                        except Exception:
                            disconnected.append(connection)
                    
                    # Remove disconnected clients
                    for connection in disconnected:
                        self.active_connections.remove(connection)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dashboard update failed: {e}")
                await asyncio.sleep(self.update_interval)

    async def _collect_dashboard_data(self) -> Dict[str, Any]:
        """Collect current dashboard data from metrics."""
        try:
            # Get basic metrics
            all_metrics = self.metrics_collector.get_all_metrics()
            
            # Calculate derived metrics
            request_rate = self._calculate_rate("http_requests_total")
            response_time = self._get_average_response_time()
            error_rate = self._calculate_error_rate()
            
            # System metrics
            memory_usage = self._get_memory_usage()
            cpu_usage = self._get_cpu_usage()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_rate": request_rate,
                "response_time": response_time,
                "error_rate": error_rate,
                "active_connections": len(self.active_connections),
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "counters": all_metrics.get("counters", {}),
                "gauges": all_metrics.get("gauges", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to collect dashboard data: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def _calculate_rate(self, metric_name: str) -> float:
        """Calculate rate per second for a counter metric."""
        summary = self.metrics_collector.get_metric_summary(
            metric_name, timedelta(minutes=1)
        )
        if summary and summary.count > 0:
            return summary.count / 60.0  # per second
        return 0.0

    def _get_average_response_time(self) -> float:
        """Get average response time in milliseconds."""
        summary = self.metrics_collector.get_metric_summary(
            "http_request_duration", timedelta(minutes=5)
        )
        if summary:
            return summary.mean * 1000  # Convert to milliseconds
        return 0.0

    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage."""
        total_requests = self.metrics_collector.counters.get("http_requests_total", 0)
        error_requests = self.metrics_collector.counters.get("http_requests_errors", 0)
        
        if total_requests > 0:
            return (error_requests / total_requests) * 100
        return 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return self.metrics_collector.gauges.get("memory_usage_mb", 0)

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=None)
        except ImportError:
            return self.metrics_collector.gauges.get("cpu_usage_percent", 0)


# Global dashboard instance
_dashboard: Optional[PerformanceDashboard] = None


def get_dashboard() -> PerformanceDashboard:
    """Get the global dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = PerformanceDashboard()
    return _dashboard
