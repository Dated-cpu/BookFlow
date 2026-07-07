"""Run use case directly to find the error."""

import asyncio
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.engine import init_db, get_session
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

async def main():
    settings = Settings()
    await init_db(settings.database_url)
    
    session_gen = get_session()
    session = await session_gen.__anext__()
    uow = SQLAlchemyUnitOfWork(session)
    
    try:
        from src.application.dtos.auth.register_user import RegisterUserRequest
        from src.application.use_cases.auth.register_user import RegisterUser
        from src.infrastructure.auth.password import BcryptPasswordHasher
        
        hasher = BcryptPasswordHasher()
        uc = RegisterUser(user_repo=uow.users, password_hasher=hasher, uow=uow)
        result = await uc.execute(RegisterUserRequest(email="direct@test.com", password="Test1234"))
        print(f"OK: {result}")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        await session_gen.aclose()

asyncio.run(main())
