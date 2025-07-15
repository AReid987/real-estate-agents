"""
Dagger CI/CD Pipeline for Real Estate Agent Marketing System
Handles building, testing, and deploying the multi-agent system
"""

import dagger
from dagger import dag, function, object_type, Container, Service, Directory
from typing import List, Optional
import asyncio

@object_type
class RealEstateAgentCI:
    """
    Dagger module for Real Estate Agent Marketing System CI/CD
    """
    
    @function
    async def build_ag2_core(self, source: Directory) -> Container:
        """
        Build the AG2 core service container
        """
        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "build-essential", "curl"])
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exposed_port(8001)
            .with_entrypoint(["python", "main.py"])
        )
    
    @function
    async def build_api_gateway(self, source: Directory) -> Container:
        """
        Build the API Gateway container
        """
        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exposed_port(8000)
            .with_entrypoint(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
        )
    
    @function
    async def build_frontend(self, source: Directory) -> Container:
        """
        Build the React frontend container
        """
        return (
            dag.container()
            .from_("node:18-alpine")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["npm", "ci"])
            .with_exec(["npm", "run", "build"])
            .from_("nginx:alpine")
            .with_directory("/usr/share/nginx/html", 
                          dag.container()
                          .from_("node:18-alpine")
                          .with_workdir("/app")
                          .with_directory("/app", source)
                          .with_exec(["npm", "ci"])
                          .with_exec(["npm", "run", "build"])
                          .directory("/app/build"))
            .with_exposed_port(80)
        )
    
    @function
    async def run_unit_tests(self, source: Directory) -> str:
        """
        Run unit tests for the AG2 core system
        """
        test_result = await (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["pip", "install", "pytest", "pytest-asyncio", "pytest-cov"])
            .with_exec(["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"])
            .stdout()
        )
        return test_result
    
    @function
    async def run_integration_tests(self, 
                                  ag2_service: Service, 
                                  langflow_service: Service,
                                  postgres_service: Service) -> str:
        """
        Run integration tests with all services running
        """
        test_result = await (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", dag.host().directory("./tests"))
            .with_service_binding("ag2", ag2_service)
            .with_service_binding("langflow", langflow_service)
            .with_service_binding("postgres", postgres_service)
            .with_exec(["pip", "install", "requests", "pytest", "pytest-asyncio"])
            .with_exec(["python", "-m", "pytest", "integration/", "-v"])
            .stdout()
        )
        return test_result
    
    @function
    async def security_scan(self, source: Directory) -> str:
        """
        Run security scans on the codebase
        """
        scan_result = await (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["pip", "install", "bandit", "safety"])
            .with_exec(["bandit", "-r", "src/", "-f", "json", "-o", "bandit-report.json"])
            .with_exec(["safety", "check", "--json", "--output", "safety-report.json"])
            .with_exec(["cat", "bandit-report.json"])
            .stdout()
        )
        return scan_result
    
    @function
    async def lint_and_format(self, source: Directory) -> str:
        """
        Run code linting and formatting checks
        """
        lint_result = await (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["pip", "install", "black", "flake8", "isort", "mypy"])
            .with_exec(["black", "--check", "src/"])
            .with_exec(["isort", "--check-only", "src/"])
            .with_exec(["flake8", "src/"])
            .with_exec(["mypy", "src/"])
            .stdout()
        )
        return lint_result
    
    @function
    async def build_and_test_complete_system(self) -> str:
        """
        Build and test the complete real estate agent system
        """
        source_dir = dag.host().directory(".")
        
        print("🏗️  Building containers...")
        
        # Build all containers
        ag2_container = await self.build_ag2_core(source_dir.directory("./ag2-core"))
        api_container = await self.build_api_gateway(source_dir.directory("./api-gateway"))
        frontend_container = await self.build_frontend(source_dir.directory("./frontend"))
        
        print("✅ Containers built successfully")
        
        # Run linting and security checks
        print("🔍 Running code quality checks...")
        lint_result = await self.lint_and_format(source_dir.directory("./ag2-core"))
        security_result = await self.security_scan(source_dir.directory("./ag2-core"))
        
        print("✅ Code quality checks passed")
        
        # Run unit tests
        print("🧪 Running unit tests...")
        unit_test_result = await self.run_unit_tests(source_dir.directory("./ag2-core"))
        
        print("✅ Unit tests passed")
        
        # Start services for integration testing
        print("🚀 Starting services for integration testing...")
        
        # PostgreSQL service
        postgres_service = (
            dag.container()
            .from_("postgres:15-alpine")
            .with_env_variable("POSTGRES_DB", "test_db")
            .with_env_variable("POSTGRES_USER", "test_user")
            .with_env_variable("POSTGRES_PASSWORD", "test_pass")
            .with_exposed_port(5432)
            .as_service()
        )
        
        # Langflow service
        langflow_service = (
            dag.container()
            .from_("langflow/langflow:latest")
            .with_env_variable("LANGFLOW_DATABASE_URL", "postgresql://test_user:test_pass@postgres:5432/test_db")
            .with_service_binding("postgres", postgres_service)
            .with_exposed_port(7860)
            .as_service()
        )
        
        # AG2 service
        ag2_service = (
            ag2_container
            .with_env_variable("DATABASE_URL", "postgresql://test_user:test_pass@postgres:5432/test_db")
            .with_env_variable("LANGFLOW_ENDPOINT", "http://langflow:7860")
            .with_service_binding("postgres", postgres_service)
            .with_service_binding("langflow", langflow_service)
            .as_service()
        )
        
        # Run integration tests
        print("🔗 Running integration tests...")
        integration_result = await self.run_integration_tests(
            ag2_service, langflow_service, postgres_service
        )
        
        print("✅ Integration tests passed")
        
        return "🎉 All tests passed! System is ready for deployment."
    
    @function
    async def deploy_to_staging(self, registry_url: str, tag: str = "latest") -> str:
        """
        Deploy the complete system to staging environment
        """
        source_dir = dag.host().directory(".")
        
        # Build containers with staging configuration
        ag2_container = await self.build_ag2_core(source_dir.directory("./ag2-core"))
        api_container = await self.build_api_gateway(source_dir.directory("./api-gateway"))
        frontend_container = await self.build_frontend(source_dir.directory("./frontend"))
        
        # Tag and push containers to registry
        ag2_ref = await ag2_container.publish(f"{registry_url}/re-ag2-core:{tag}")
        api_ref = await api_container.publish(f"{registry_url}/re-api-gateway:{tag}")
        frontend_ref = await frontend_container.publish(f"{registry_url}/re-frontend:{tag}")
        
        # Deploy using Docker Compose
        deploy_result = await (
            dag.container()
            .from_("docker/compose:latest")
            .with_directory("/deploy", source_dir)
            .with_workdir("/deploy")
            .with_env_variable("AG2_IMAGE", ag2_ref)
            .with_env_variable("API_IMAGE", api_ref)
            .with_env_variable("FRONTEND_IMAGE", frontend_ref)
            .with_env_variable("ENVIRONMENT", "staging")
            .with_exec(["docker-compose", "-f", "docker-compose.staging.yml", "up", "-d"])
            .stdout()
        )
        
        return f"🚀 Deployed to staging:\nAG2: {ag2_ref}\nAPI: {api_ref}\nFrontend: {frontend_ref}"
    
    @function
    async def deploy_to_production(self, 
                                 registry_url: str, 
                                 tag: str = "latest",
                                 approval_token: str = "") -> str:
        """
        Deploy to production with additional safety checks
        """
        if not approval_token or approval_token != "APPROVED_FOR_PRODUCTION":
            return "❌ Production deployment requires approval token"
        
        source_dir = dag.host().directory(".")
        
        # Run complete test suite before production deployment
        test_result = await self.build_and_test_complete_system()
        
        if "All tests passed" not in test_result:
            return "❌ Tests failed. Cannot deploy to production."
        
        # Build production containers with optimizations
        ag2_container = (
            await self.build_ag2_core(source_dir.directory("./ag2-core"))
            .with_env_variable("ENVIRONMENT", "production")
            .with_env_variable("LOG_LEVEL", "WARNING")
        )
        
        api_container = (
            await self.build_api_gateway(source_dir.directory("./api-gateway"))
            .with_env_variable("ENVIRONMENT", "production")
        )
        
        frontend_container = await self.build_frontend(source_dir.directory("./frontend"))
        
        # Push to production registry
        ag2_prod_ref = await ag2_container.publish(f"{registry_url}/re-ag2-core:prod-{tag}")
        api_prod_ref = await api_container.publish(f"{registry_url}/re-api-gateway:prod-{tag}")
        frontend_prod_ref = await frontend_container.publish(f"{registry_url}/re-frontend:prod-{tag}")
        
        # Production deployment with health checks
        deploy_result = await (
            dag.container()
            .from_("docker/compose:latest")
            .with_directory("/deploy", source_dir)
            .with_workdir("/deploy")
            .with_env_variable("AG2_IMAGE", ag2_prod_ref)
            .with_env_variable("API_IMAGE", api_prod_ref)
            .with_env_variable("FRONTEND_IMAGE", frontend_prod_ref)
            .with_env_variable("ENVIRONMENT", "production")
            .with_exec(["docker-compose", "-f", "docker-compose.production.yml", "up", "-d"])
            .with_exec(["sleep", "30"])  # Wait for services to start
            .with_exec(["docker-compose", "-f", "docker-compose.production.yml", "ps"])
            .stdout()
        )
        
        return f"🎉 Successfully deployed to production:\nAG2: {ag2_prod_ref}\nAPI: {api_prod_ref}\nFrontend: {frontend_prod_ref}"
    
    @function
    async def run_performance_tests(self, target_url: str) -> str:
        """
        Run performance tests against deployed system
        """
        perf_result = await (
            dag.container()
            .from_("loadimpact/k6:latest")
            .with_directory("/scripts", dag.host().directory("./performance-tests"))
            .with_env_variable("TARGET_URL", target_url)
            .with_exec(["k6", "run", "--vus", "10", "--duration", "30s", "/scripts/load-test.js"])
            .stdout()
        )
        return perf_result
    
    @function
    async def backup_database(self, db_url: str) -> str:
        """
        Create database backup before deployment
        """
        backup_result = await (
            dag.container()
            .from_("postgres:15-alpine")
            .with_env_variable("DATABASE_URL", db_url)
            .with_exec(["pg_dump", db_url, "-f", f"/backup/backup-{dag.current_module().name()}.sql"])
            .stdout()
        )
        return backup_result
    
    @function
    async def rollback_deployment(self, previous_tag: str, registry_url: str) -> str:
        """
        Rollback to previous deployment version
        """
        rollback_result = await (
            dag.container()
            .from_("docker/compose:latest")
            .with_directory("/deploy", dag.host().directory("."))
            .with_workdir("/deploy")
            .with_env_variable("AG2_IMAGE", f"{registry_url}/re-ag2-core:{previous_tag}")
            .with_env_variable("API_IMAGE", f"{registry_url}/re-api-gateway:{previous_tag}")
            .with_env_variable("FRONTEND_IMAGE", f"{registry_url}/re-frontend:{previous_tag}")
            .with_exec(["docker-compose", "down"])
            .with_exec(["docker-compose", "up", "-d"])
            .stdout()
        )
        return f"🔄 Rolled back to version {previous_tag}"
    
    @function
    async def health_check(self, services: List[str]) -> str:
        """
        Comprehensive health check for all services
        """
        health_results = []
        
        for service in services:
            if service == "ag2-core":
                result = await (
                    dag.container()
                    .from_("curlimages/curl:latest")
                    .with_exec(["curl", "-f", "http://ag2-core:8001/health"])
                    .stdout()
                )
                health_results.append(f"AG2 Core: {result}")
            
            elif service == "api-gateway":
                result = await (
                    dag.container()
                    .from_("curlimages/curl:latest")
                    .with_exec(["curl", "-f", "http://api-gateway:8000/health"])
                    .stdout()
                )
                health_results.append(f"API Gateway: {result}")
            
            elif service == "langflow":
                result = await (
                    dag.container()
                    .from_("curlimages/curl:latest")
                    .with_exec(["curl", "-f", "http://langflow:7860/health"])
                    .stdout()
                )
                health_results.append(f"Langflow: {result}")
        
        return "\\n".join(health_results)

# Example usage functions
@function
async def ci_pipeline() -> str:
    """
    Complete CI pipeline for real estate agent system
    """
    ci = RealEstateAgentCI()
    
    print("🚀 Starting CI Pipeline...")
    
    # Run complete build and test
    result = await ci.build_and_test_complete_system()
    
    print("✅ CI Pipeline completed successfully")
    return result

@function
async def cd_pipeline_staging(registry_url: str) -> str:
    """
    CD pipeline for staging deployment
    """
    ci = RealEstateAgentCI()
    
    print("🎯 Starting Staging Deployment...")
    
    # Deploy to staging
    result = await ci.deploy_to_staging(registry_url, "staging-latest")
    
    # Run health checks
    health_result = await ci.health_check(["ag2-core", "api-gateway", "langflow"])
    
    return f"{result}\\n\\nHealth Check Results:\\n{health_result}"

@function
async def cd_pipeline_production(registry_url: str, approval_token: str) -> str:
    """
    CD pipeline for production deployment
    """
    ci = RealEstateAgentCI()
    
    print("🏭 Starting Production Deployment...")
    
    # Deploy to production
    result = await ci.deploy_to_production(registry_url, "prod-latest", approval_token)
    
    if "Successfully deployed" in result:
        # Run performance tests
        perf_result = await ci.run_performance_tests("https://production-url.com")
        result += f"\\n\\nPerformance Test Results:\\n{perf_result}"
    
    return result

# Main function for testing locally
async def main():
    """Test the Dagger pipeline locally"""
    ci = RealEstateAgentCI()
    
    # Run CI pipeline
    result = await ci.build_and_test_complete_system()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())