import asyncio
from app.database.connection import get_db
from app.database.seeds.seeder import Seeder

async def run_seeder():
    print("🌱 Seeding started")
    try:
        async for db in get_db():
            seeder = Seeder(db)
            success = await seeder.seed_all()
            if success:
                await db.commit()
                print("✅ Seeding completed")
            else:
                await db.rollback()
                print("❌ Seeding failed")
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    asyncio.run(run_seeder())