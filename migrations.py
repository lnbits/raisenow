# the migration file is where you build your database tables
# If you create a new release for your extension , remeember the migration file is like a blockchain, never edit only add!


async def m001_initial(db):
    """
    Initial raises table. Includes lnurlpay for donating to all participants.
    """
    await db.execute(
        """
        CREATE TABLE raisenow.raises (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            background_image TEXT NOT NULL,
            header_image TEXT NOT NULL,
            description TEXT NOT NULL,
            live_dates TEXT NOT NULL,
            total INTEGER DEFAULT 0,
            lnurlpay TEXT
        );
    """
    )

async def m002_initial(db):
    """
    Initial templates table.
    """
    await db.execute(
        """
        CREATE TABLE raisenow.participants (
            id TEXT PRIMARY KEY,
            raise TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            total INTEGER DEFAULT 0,
            lnurlpay TEXT
        );
    """
    )
