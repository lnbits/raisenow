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


async def m003_drop_lnurlpay(db):
    """
    Migration to drop lnurlpay columns from raisenow.raises and raisenow.participants.
    """
    # Drop lnurlpay from raisenow.raises
    await db.execute(
        """
        ALTER TABLE raisenow.raises
        DROP COLUMN lnurlpay;
        """
    )

    # Drop lnurlpay from raisenow.participants
    await db.execute(
        """
        ALTER TABLE raisenow.participants
        DROP COLUMN lnurlpay;
        """
    )


async def m004_add_lnurlpay(db):
    """
    Add timestamp to templates table.
    """
    await db.execute(
        """
        ALTER TABLE raisenow.participants
        ADD COLUMN lnurlpay TEXT;
    """
    )
    await db.execute(
        """
        ALTER TABLE raisenow.raises
        ADD COLUMN lnurlpay TEXT;
    """
    )
