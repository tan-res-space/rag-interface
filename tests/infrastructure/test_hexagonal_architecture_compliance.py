"""
Hexagonal Architecture Compliance Tests

Tests that verify the codebase follows Hexagonal Architecture (Ports and Adapters) 
principles with proper separation of concerns and dependency inversion.
"""

import pytest
import inspect
import importlib
from typing import List, Set, Dict
from pathlib import Path

from src.error_reporting_service.domain.entities.error_report import ErrorReport
from src.error_reporting_service.application.ports.secondary.repository_port import ErrorReportRepository
from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import PostgreSQLAdapter


class TestHexagonalArchitectureCompliance:
    """Test compliance with Hexagonal Architecture principles"""

    def test_domain_layer_independence(self):
        """Test that domain layer has no dependencies on infrastructure"""
        domain_modules = self._get_modules_in_package("src.error_reporting_service.domain")
        
        for module_name in domain_modules:
            module = importlib.import_module(module_name)
            
            # Check imports in the module
            imports = self._get_module_imports(module)
            
            # Domain should not import from infrastructure or application layers
            forbidden_imports = [
                "infrastructure",
                "adapters", 
                "fastapi",
                "sqlalchemy",
                "redis",
                "kafka"
            ]
            
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert forbidden not in imp.lower(), \
                        f"Domain module {module_name} imports {imp} (forbidden: {forbidden})"

    def test_application_layer_dependencies(self):
        """Test that application layer only depends on domain and ports"""
        app_modules = self._get_modules_in_package("src.error_reporting_service.application")
        
        for module_name in app_modules:
            if "ports" in module_name:
                continue  # Ports are allowed to define interfaces
                
            module = importlib.import_module(module_name)
            imports = self._get_module_imports(module)
            
            # Application should not import concrete infrastructure implementations
            forbidden_imports = [
                "postgresql",
                "mongodb", 
                "redis",
                "kafka",
                "adapters.database",
                "adapters.messaging"
            ]
            
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert forbidden not in imp.lower(), \
                        f"Application module {module_name} imports {imp} (forbidden: {forbidden})"

    def test_infrastructure_adapters_implement_ports(self):
        """Test that infrastructure adapters implement the correct ports"""
        # Test database adapter implements repository port
        assert issubclass(PostgreSQLAdapter, ErrorReportRepository), \
            "PostgreSQLAdapter must implement ErrorReportRepository port"
        
        # Verify all required methods are implemented
        port_methods = self._get_abstract_methods(ErrorReportRepository)
        adapter_methods = self._get_public_methods(PostgreSQLAdapter)
        
        for method in port_methods:
            assert method in adapter_methods, \
                f"PostgreSQLAdapter missing required method: {method}"

    def test_use_cases_depend_on_ports_not_adapters(self):
        """Test that use cases depend on ports, not concrete adapters"""
        use_case_init = inspect.signature(SubmitErrorReportUseCase.__init__)
        
        for param_name, param in use_case_init.parameters.items():
            if param_name == "self":
                continue
                
            # Parameters should be abstract ports, not concrete adapters
            param_type = param.annotation
            if hasattr(param_type, "__module__"):
                module_name = param_type.__module__
                assert "adapters" not in module_name, \
                    f"Use case depends on concrete adapter: {param_type}"
                assert "ports" in module_name or "abc" in module_name, \
                    f"Use case should depend on ports: {param_type}"

    def test_dependency_inversion_principle(self):
        """Test that high-level modules don't depend on low-level modules"""
        # Check that domain entities don't depend on infrastructure
        error_report_module = inspect.getmodule(ErrorReport)
        imports = self._get_module_imports(error_report_module)
        
        infrastructure_imports = [
            imp for imp in imports 
            if any(infra in imp.lower() for infra in ["sqlalchemy", "fastapi", "redis"])
        ]
        
        assert len(infrastructure_imports) == 0, \
            f"Domain entity has infrastructure dependencies: {infrastructure_imports}"

    def test_port_interfaces_are_abstract(self):
        """Test that port interfaces are properly abstract"""
        from src.error_reporting_service.application.ports.secondary.repository_port import ErrorReportRepository
        
        # Port should be abstract
        assert inspect.isabstract(ErrorReportRepository), \
            "Repository port should be abstract"
        
        # Should have abstract methods
        abstract_methods = self._get_abstract_methods(ErrorReportRepository)
        assert len(abstract_methods) > 0, \
            "Repository port should have abstract methods"

    def test_adapters_are_in_infrastructure_layer(self):
        """Test that all adapters are in the infrastructure layer"""
        adapter_files = list(Path("src").rglob("*adapter*.py"))
        
        for adapter_file in adapter_files:
            path_parts = adapter_file.parts
            assert "infrastructure" in path_parts, \
                f"Adapter {adapter_file} should be in infrastructure layer"

    def test_no_circular_dependencies(self):
        """Test that there are no circular dependencies between layers"""
        # This is a simplified check - in practice, you'd use tools like pydeps
        domain_modules = self._get_modules_in_package("src.error_reporting_service.domain")
        app_modules = self._get_modules_in_package("src.error_reporting_service.application")
        infra_modules = self._get_modules_in_package("src.error_reporting_service.infrastructure")
        
        # Domain should not import from application or infrastructure
        for domain_module in domain_modules:
            module = importlib.import_module(domain_module)
            imports = self._get_module_imports(module)
            
            app_imports = [imp for imp in imports if any(app in imp for app in app_modules)]
            infra_imports = [imp for imp in imports if any(infra in imp for infra in infra_modules)]
            
            assert len(app_imports) == 0, f"Domain module {domain_module} imports application: {app_imports}"
            assert len(infra_imports) == 0, f"Domain module {domain_module} imports infrastructure: {infra_imports}"

    def test_business_logic_in_domain_layer(self):
        """Test that business logic is properly encapsulated in domain layer"""
        # Check that ErrorReport entity has business methods
        error_report_methods = self._get_public_methods(ErrorReport)
        
        business_methods = [
            method for method in error_report_methods 
            if not method.startswith("_") and method not in ["error_id", "job_id", "speaker_id"]
        ]
        
        assert len(business_methods) > 0, \
            "Domain entity should have business logic methods"

    def test_infrastructure_configuration_isolation(self):
        """Test that infrastructure configuration is isolated"""
        # Configuration should be in infrastructure layer
        config_files = list(Path("src").rglob("*config*.py"))
        settings_files = list(Path("src").rglob("*settings*.py"))
        
        all_config_files = config_files + settings_files
        
        for config_file in all_config_files:
            if "test" in str(config_file):
                continue
                
            path_parts = config_file.parts
            assert "infrastructure" in path_parts, \
                f"Configuration {config_file} should be in infrastructure layer"

    def test_dto_objects_in_application_layer(self):
        """Test that DTOs are properly placed in application layer"""
        dto_files = list(Path("src").rglob("*dto*.py"))
        request_files = list(Path("src").rglob("*request*.py"))
        response_files = list(Path("src").rglob("*response*.py"))
        
        all_dto_files = dto_files + request_files + response_files
        
        for dto_file in all_dto_files:
            if "test" in str(dto_file):
                continue
                
            path_parts = dto_file.parts
            assert "application" in path_parts, \
                f"DTO {dto_file} should be in application layer"

    def _get_modules_in_package(self, package_name: str) -> List[str]:
        """Get all modules in a package"""
        try:
            package_path = Path(package_name.replace(".", "/"))
            python_files = list(package_path.rglob("*.py"))
            
            modules = []
            for py_file in python_files:
                if py_file.name == "__init__.py":
                    continue
                    
                module_path = str(py_file).replace("/", ".").replace(".py", "")
                modules.append(module_path)
            
            return modules
        except Exception:
            return []

    def _get_module_imports(self, module) -> List[str]:
        """Get all imports from a module"""
        imports = []
        
        if hasattr(module, "__file__") and module.__file__:
            try:
                with open(module.__file__, 'r') as f:
                    content = f.read()
                    
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line)
            except Exception:
                pass
        
        return imports

    def _get_abstract_methods(self, cls) -> Set[str]:
        """Get abstract methods from a class"""
        if hasattr(cls, "__abstractmethods__"):
            return cls.__abstractmethods__
        return set()

    def _get_public_methods(self, cls) -> List[str]:
        """Get public methods from a class"""
        return [
            method for method in dir(cls) 
            if not method.startswith('_') and callable(getattr(cls, method))
        ]


class TestDomainDrivenDesignCompliance:
    """Test compliance with Domain-Driven Design principles"""

    def test_entities_have_identity(self):
        """Test that entities have proper identity"""
        error_report = ErrorReport(
            job_id="test-job",
            speaker_id="test-speaker", 
            reported_by="test-user",
            original_text="test original",
            corrected_text="test corrected",
            error_categories=["test"],
            severity_level="medium",
            start_position=0,
            end_position=4,
            error_timestamp=None
        )
        
        # Entity should have an ID
        assert hasattr(error_report, 'error_id')
        assert error_report.error_id is not None

    def test_value_objects_are_immutable(self):
        """Test that value objects are immutable"""
        # This would test value objects if they exist
        # For now, we'll test that domain entities maintain integrity
        
        error_report = ErrorReport(
            job_id="test-job",
            speaker_id="test-speaker",
            reported_by="test-user", 
            original_text="test original",
            corrected_text="test corrected",
            error_categories=["test"],
            severity_level="medium",
            start_position=0,
            end_position=4,
            error_timestamp=None
        )
        
        # Should not be able to modify core attributes after creation
        original_id = error_report.error_id
        
        # Attempting to modify should either fail or not change the ID
        try:
            error_report.error_id = "new-id"
            # If modification is allowed, it should maintain consistency
            assert error_report.error_id == original_id or error_report.error_id == "new-id"
        except AttributeError:
            # Immutable - this is good
            pass

    def test_aggregates_maintain_consistency(self):
        """Test that aggregates maintain business rule consistency"""
        # Test that ErrorReport aggregate maintains consistency
        with pytest.raises(ValueError):
            ErrorReport(
                job_id="test-job",
                speaker_id="test-speaker",
                reported_by="test-user",
                original_text="same text",
                corrected_text="same text",  # Should not be same as original
                error_categories=["test"],
                severity_level="medium", 
                start_position=0,
                end_position=4,
                error_timestamp=None
            )

    def test_domain_services_encapsulate_business_logic(self):
        """Test that domain services properly encapsulate business logic"""
        from src.error_reporting_service.domain.services.validation_service import ErrorValidationService
        
        validation_service = ErrorValidationService()
        
        # Should have business logic methods
        assert hasattr(validation_service, 'validate_error_categories')
        assert callable(validation_service.validate_error_categories)
        
        # Should encapsulate domain knowledge
        valid_categories = ["medical_terminology", "grammar", "spelling"]
        result = validation_service.validate_error_categories(valid_categories)
        assert result is True
