from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.models import Repository, Error
from app.database.session import SessionLocal
from app.api.models import RepositoryCreate, ErrorCreate
from app.utils.logger import setup_logger, log_error

logger = setup_logger(__name__)


class RepositoryOperations:
    """Database operations for Repository model."""
    
    @staticmethod
    async def create_repository(repo_data: RepositoryCreate) -> Optional[Repository]:
        """
        Create a new repository record.
        
        Args:
            repo_data: Repository creation data
            
        Returns:
            Created Repository object or None if failed
        """
        try:
            async with SessionLocal() as session:
                db_repo = Repository(
                    name=repo_data.name,
                    url=repo_data.url
                )
                session.add(db_repo)
                await session.commit()
                await session.refresh(db_repo)
                logger.info(f"Created repository: {repo_data.name}")
                return db_repo
        except IntegrityError as e:
            logger.warning(f"Repository creation failed - integrity error: {str(e)}")
            return None
        except SQLAlchemyError as e:
            log_error(e, "create_repository")
            return None
    
    @staticmethod
    async def get_repository(repo_id: int) -> Optional[Repository]:
        """
        Get repository by ID.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Repository object or None if not found
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Repository).where(Repository.id == repo_id)
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log_error(e, "get_repository")
            return None
    
    @staticmethod
    async def get_repository_by_name(name: str) -> Optional[Repository]:
        """
        Get repository by name.
        
        Args:
            name: Repository name
            
        Returns:
            Repository object or None if not found
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Repository).where(Repository.name == name)
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log_error(e, "get_repository_by_name")
            return None
    
    @staticmethod
    async def list_repositories(limit: int = 100, offset: int = 0) -> List[Repository]:
        """
        List repositories with pagination.
        
        Args:
            limit: Maximum number of repositories to return
            offset: Number of repositories to skip
            
        Returns:
            List of Repository objects
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Repository).offset(offset).limit(limit)
                )
                return result.scalars().all()
        except SQLAlchemyError as e:
            log_error(e, "list_repositories")
            return []
    
    @staticmethod
    async def update_repository(repo_id: int, repo_data: RepositoryCreate) -> Optional[Repository]:
        """
        Update repository.
        
        Args:
            repo_id: Repository ID
            repo_data: Updated repository data
            
        Returns:
            Updated Repository object or None if failed
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Repository).where(Repository.id == repo_id)
                )
                db_repo = result.scalar_one_or_none()
                
                if not db_repo:
                    return None
                
                db_repo.name = repo_data.name
                db_repo.url = repo_data.url
                
                await session.commit()
                await session.refresh(db_repo)
                logger.info(f"Updated repository: {repo_id}")
                return db_repo
        except SQLAlchemyError as e:
            log_error(e, "update_repository")
            return None
    
    @staticmethod
    async def delete_repository(repo_id: int) -> bool:
        """
        Delete repository.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            True if deleted, False if not found or failed
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    delete(Repository).where(Repository.id == repo_id)
                )
                await session.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Deleted repository: {repo_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            log_error(e, "delete_repository")
            return False


class ErrorOperations:
    """Database operations for Error model."""
    
    @staticmethod
    async def create_error(error_data: ErrorCreate) -> Optional[Error]:
        """
        Create a new error record.
        
        Args:
            error_data: Error creation data
            
        Returns:
            Created Error object or None if failed
        """
        try:
            async with SessionLocal() as session:
                db_error = Error(message=error_data.message)
                session.add(db_error)
                await session.commit()
                await session.refresh(db_error)
                logger.info(f"Created error record: {len(error_data.message)} chars")
                return db_error
        except SQLAlchemyError as e:
            log_error(e, "create_error")
            return None
    
    @staticmethod
    async def get_error(error_id: int) -> Optional[Error]:
        """
        Get error by ID.
        
        Args:
            error_id: Error ID
            
        Returns:
            Error object or None if not found
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Error).where(Error.id == error_id)
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log_error(e, "get_error")
            return None
    
    @staticmethod
    async def list_errors(limit: int = 100, offset: int = 0) -> List[Error]:
        """
        List errors with pagination, newest first.
        
        Args:
            limit: Maximum number of errors to return
            offset: Number of errors to skip
            
        Returns:
            List of Error objects
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    select(Error)
                    .order_by(Error.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
                return result.scalars().all()
        except SQLAlchemyError as e:
            log_error(e, "list_errors")
            return []
    
    @staticmethod
    async def delete_error(error_id: int) -> bool:
        """
        Delete error record.
        
        Args:
            error_id: Error ID
            
        Returns:
            True if deleted, False if not found or failed
        """
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    delete(Error).where(Error.id == error_id)
                )
                await session.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Deleted error: {error_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            log_error(e, "delete_error")
            return False


# Create instances for easy import
repository_ops = RepositoryOperations()
error_ops = ErrorOperations()