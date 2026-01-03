#[cfg(feature = "mongodb")]
use mongodb::{Client as MongoClient, options::ClientOptions as MongoClientOptions};

#[cfg(feature = "polodb")]
use polodb_core::Database as PoloDatabase;

#[cfg(feature = "polodb")]
use std::sync::Arc;

use crate::config::Settings;

#[derive(Clone, Default)]
pub struct DbHandles {
    #[cfg(feature = "polodb")]
    pub polodb: Option<Arc<PoloDatabase>>,
    #[cfg(feature = "mongodb")]
    pub mongo: Option<MongoClient>,
}

#[cfg(feature = "mongodb")]
async fn create_mongo_client(url: &str) -> anyhow::Result<MongoClient> {
    let opts = MongoClientOptions::parse(url).await?;
    Ok(MongoClient::with_options(opts)?)
}

/// Initializes the database using loaded settings. If use_embedded_postgres is enabled,
/// starts an embedded PostgreSQL instance and connects to it; otherwise falls back to db_url logic.
pub async fn init_db_with_settings(settings: &Settings) -> anyhow::Result<DbHandles> {
    dotenv::dotenv().ok();

    #[cfg(feature = "polodb")]
    {
        // Default storage: PoloDB file. Use db_url as path (or polodb://<path>).
        let mut path = settings.db_url();
        if let Some(rest) = path.strip_prefix("polodb://") {
            path = rest.to_string();
        }
        let db = PoloDatabase::open_path(&path)?;
        let polodb = Some(Arc::new(db));

        // If storage explicitly asks for mongodb and feature is enabled, also init mongo.
        #[cfg(feature = "mongodb")]
        {
            if settings.storage() == "mongodb" {
                let mongo_url = settings.db_url();
                let mongo = create_mongo_client(&mongo_url).await?;
                return Ok(DbHandles { polodb, mongo: Some(mongo) });
            }
        }

        return Ok(DbHandles {
            polodb,
            #[cfg(feature = "mongodb")]
            mongo: None,
        });
    }

    #[cfg(feature = "mongodb")]
    {
        // Use db_url as Mongo URI.
        let mongo_url = settings.db_url();
        let mongo = create_mongo_client(&mongo_url).await?;
        return Ok(DbHandles {
            #[cfg(feature = "polodb")]
            polodb: None,
            mongo: Some(mongo),
        });
    }

    #[cfg(not(feature = "mongodb"))]
    {
        let _ = settings;
        return Ok(DbHandles::default());
    }
}
