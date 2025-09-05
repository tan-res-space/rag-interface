"""
Speaker Metrics Value Object
Encapsulates speaker performance metrics and calculations
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics


@dataclass(frozen=True)
class SpeakerMetrics:
    """
    Immutable value object containing speaker performance metrics
    """
    total_reports: int
    total_errors_found: int
    total_corrections_made: int
    average_error_rate: float
    average_correction_accuracy: float
    last_report_date: Optional[datetime] = None
    reports_last_30_days: int = 0
    errors_last_30_days: int = 0
    corrections_last_30_days: int = 0
    consistency_score: float = 0.0
    improvement_trend: float = 0.0
    
    def __post_init__(self):
        """Validate metrics data"""
        if self.total_reports < 0:
            raise ValueError("Total reports cannot be negative")
        
        if self.total_errors_found < 0:
            raise ValueError("Total errors found cannot be negative")
            
        if self.total_corrections_made < 0:
            raise ValueError("Total corrections made cannot be negative")
        
        if not (0.0 <= self.average_error_rate <= 1.0):
            raise ValueError("Average error rate must be between 0.0 and 1.0")
            
        if not (0.0 <= self.average_correction_accuracy <= 1.0):
            raise ValueError("Average correction accuracy must be between 0.0 and 1.0")
    
    @classmethod
    def calculate_from_reports(cls, reports: List[Dict[str, Any]]) -> 'SpeakerMetrics':
        """Calculate metrics from a list of error reports"""
        if not reports:
            return cls(
                total_reports=0,
                total_errors_found=0,
                total_corrections_made=0,
                average_error_rate=0.0,
                average_correction_accuracy=0.0
            )
        
        total_reports = len(reports)
        total_errors = sum(1 for report in reports if report.get('error_categories'))
        total_corrections = sum(1 for report in reports if report.get('corrected_text'))
        
        # Calculate error rates for each report
        error_rates = []
        correction_accuracies = []
        
        for report in reports:
            # Calculate error rate based on text length and errors found
            original_text = report.get('original_text', '')
            corrected_text = report.get('corrected_text', '')
            
            if original_text:
                # Simple error rate calculation based on character differences
                error_rate = cls._calculate_error_rate(original_text, corrected_text)
                error_rates.append(error_rate)
                
                # Calculate correction accuracy based on quality of correction
                accuracy = cls._calculate_correction_accuracy(report)
                correction_accuracies.append(accuracy)
        
        avg_error_rate = statistics.mean(error_rates) if error_rates else 0.0
        avg_correction_accuracy = statistics.mean(correction_accuracies) if correction_accuracies else 0.0
        
        # Calculate recent activity (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_reports = [
            r for r in reports 
            if r.get('created_at') and datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) > cutoff_date
        ]
        
        reports_last_30_days = len(recent_reports)
        errors_last_30_days = sum(1 for r in recent_reports if r.get('error_categories'))
        corrections_last_30_days = sum(1 for r in recent_reports if r.get('corrected_text'))
        
        # Calculate consistency score (lower variance = higher consistency)
        consistency_score = cls._calculate_consistency_score(error_rates)
        
        # Calculate improvement trend
        improvement_trend = cls._calculate_improvement_trend(reports)
        
        # Get last report date
        last_report_date = None
        if reports:
            sorted_reports = sorted(
                reports, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )
            if sorted_reports[0].get('created_at'):
                last_report_date = datetime.fromisoformat(
                    sorted_reports[0]['created_at'].replace('Z', '+00:00')
                )
        
        return cls(
            total_reports=total_reports,
            total_errors_found=total_errors,
            total_corrections_made=total_corrections,
            average_error_rate=avg_error_rate,
            average_correction_accuracy=avg_correction_accuracy,
            last_report_date=last_report_date,
            reports_last_30_days=reports_last_30_days,
            errors_last_30_days=errors_last_30_days,
            corrections_last_30_days=corrections_last_30_days,
            consistency_score=consistency_score,
            improvement_trend=improvement_trend
        )
    
    @staticmethod
    def _calculate_error_rate(original_text: str, corrected_text: str) -> float:
        """Calculate error rate based on text differences"""
        if not original_text:
            return 0.0
        
        # Simple character-based difference calculation
        original_len = len(original_text)
        corrected_len = len(corrected_text)
        
        # Calculate Levenshtein distance approximation
        max_len = max(original_len, corrected_len)
        if max_len == 0:
            return 0.0
        
        # Simple difference ratio
        diff_ratio = abs(original_len - corrected_len) / max_len
        
        # Cap at 1.0 and ensure reasonable error rate
        return min(diff_ratio, 1.0)
    
    @staticmethod
    def _calculate_correction_accuracy(report: Dict[str, Any]) -> float:
        """Calculate correction accuracy based on report quality"""
        # Base accuracy score
        accuracy = 0.5
        
        # Bonus for having corrected text
        if report.get('corrected_text'):
            accuracy += 0.2
        
        # Bonus for having context notes
        if report.get('context_notes'):
            accuracy += 0.1
        
        # Bonus for categorizing errors
        if report.get('error_categories'):
            accuracy += 0.1
        
        # Bonus for severity assessment
        if report.get('severity_level'):
            accuracy += 0.1
        
        return min(accuracy, 1.0)
    
    @staticmethod
    def _calculate_consistency_score(error_rates: List[float]) -> float:
        """Calculate consistency score based on error rate variance"""
        if len(error_rates) < 2:
            return 1.0
        
        variance = statistics.variance(error_rates)
        # Convert variance to consistency score (lower variance = higher consistency)
        consistency = max(0.0, 1.0 - variance)
        return consistency
    
    @staticmethod
    def _calculate_improvement_trend(reports: List[Dict[str, Any]]) -> float:
        """Calculate improvement trend over time"""
        if len(reports) < 3:
            return 0.0
        
        # Sort reports by date
        sorted_reports = sorted(
            reports,
            key=lambda x: x.get('created_at', ''),
            reverse=False
        )
        
        # Calculate error rates for first and last third of reports
        third = len(sorted_reports) // 3
        early_reports = sorted_reports[:third]
        recent_reports = sorted_reports[-third:]
        
        early_error_rates = [
            SpeakerMetrics._calculate_error_rate(
                r.get('original_text', ''), 
                r.get('corrected_text', '')
            ) for r in early_reports
        ]
        
        recent_error_rates = [
            SpeakerMetrics._calculate_error_rate(
                r.get('original_text', ''), 
                r.get('corrected_text', '')
            ) for r in recent_reports
        ]
        
        if not early_error_rates or not recent_error_rates:
            return 0.0
        
        early_avg = statistics.mean(early_error_rates)
        recent_avg = statistics.mean(recent_error_rates)
        
        # Positive trend means improvement (lower recent error rate)
        if early_avg == 0:
            return 0.0
        
        improvement = (early_avg - recent_avg) / early_avg
        return max(-1.0, min(1.0, improvement))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "total_reports": self.total_reports,
            "total_errors_found": self.total_errors_found,
            "total_corrections_made": self.total_corrections_made,
            "average_error_rate": round(self.average_error_rate, 4),
            "average_correction_accuracy": round(self.average_correction_accuracy, 4),
            "last_report_date": self.last_report_date.isoformat() if self.last_report_date else None,
            "reports_last_30_days": self.reports_last_30_days,
            "errors_last_30_days": self.errors_last_30_days,
            "corrections_last_30_days": self.corrections_last_30_days,
            "consistency_score": round(self.consistency_score, 4),
            "improvement_trend": round(self.improvement_trend, 4)
        }
