async def m001_initial(db):
    """
    Initial raises table. Includes lnurlpay for donating to all participants.
    """
    await db.execute(
        """
        CREATE TABLE raisenow.raises (
            id TEXT PRIMARY KEY NOT NULL,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            background_image TEXT,
            header_image TEXT,
            live_dates TEXT,
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
            id TEXT PRIMARY KEY NOT NULL,
            raisenow TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            profile_image TEXT,
            lnaddress TEXT,
            total INTEGER DEFAULT 0,
            lnurlpay TEXT
        );
    """
    )
