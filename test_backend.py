import asyncio
import httpx
import traceback

async def main():
    # Direct import test
    import sys
    sys.path.insert(0, "C:\\Users\\Даня\\Desktop\\AI\\experements\\bookflow-ai")
    
    from src.infrastructure.config.settings import Settings
    from src.infrastructure.database.engine import init_db, get_session
    from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
    from src.application.dtos.auth.register_user import RegisterUserRequest
    from src.application.use_cases.auth.register_user import RegisterUser
    from src.infrastructure.auth.password import BcryptPasswordHasher

    settings = Settings()
    await init_db(settings.database_url)
    
    session_gen = get_session()
    session = await session_gen.__anext__()
    uow = SQLAlchemyUnitOfWork(session)
    
    try:
        hasher = BcryptPasswordHasher()
        uc = RegisterUser(user_repo=uow.users, password_hasher=hasher, uow=uow)
        result = await uc.execute(RegisterUserRequest(email="direct@test.com", password="Test1234"))
        print(f"Register OK: {result}")
    except Exception as e:
        traceback.print_exc()
    finally:
        await session_gen.aclose()

asyncio.run(main())
