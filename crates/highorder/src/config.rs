use serde::Deserialize;

#[derive(Debug, Clone, Deserialize, Default)]
pub struct SetupKey {
    pub client_key: String,
    pub client_secret: String,
}

#[derive(Debug, Clone, Deserialize, Default)]
pub struct Settings {
    pub debug: Option<bool>,
    pub host: Option<String>,
    pub port: Option<u16>,
    pub run_editor: Option<bool>,
    pub db_url: Option<String>,
    pub data_dir: Option<String>,
    pub content_url: Option<String>,
    pub webapp_root: Option<String>,
    pub setup_keys: Option<Vec<SetupKey>>,
    // Embedded Postgres options
    pub use_embedded_postgres: Option<bool>,
    pub embedded_pg_data_dir: Option<String>,
    pub embedded_pg_port: Option<u16>,
}

impl Settings {
    pub fn load() -> anyhow::Result<Self> {
        let mut builder = config::Config::builder();
        builder = builder.add_source(config::File::with_name("settings").required(false));
        builder = builder.add_source(config::Environment::with_prefix("HIGHORDER").separator("__"));
        let cfg = builder.build()?;
        let settings: Settings = cfg.try_deserialize()?;
        Ok(settings)
    }

    pub fn debug(&self) -> bool { self.debug.unwrap_or(false) }
    pub fn host(&self) -> String { self.host.clone().unwrap_or_else(|| "0.0.0.0".to_string()) }
    pub fn port(&self) -> u16 { self.port.unwrap_or(9000) }
    pub fn run_editor(&self) -> bool { self.run_editor.unwrap_or(false) }
    pub fn db_url(&self) -> String {
        self.db_url
            .clone()
            .unwrap_or_else(|| "sqlite://./highorder.db?mode=rwc".to_string())
    }

    // Whether to use embedded Postgres. If explicitly set, honor it.
    // Otherwise, default to true when db_url is not provided.
    pub fn use_embedded_postgres(&self) -> bool {
        match self.use_embedded_postgres {
            Some(b) => b,
            None => self.db_url.is_none(),
        }
    }

    pub fn embedded_pg_data_dir(&self) -> String {
        self.embedded_pg_data_dir
            .clone()
            .unwrap_or_else(|| "./.pg-data".to_string())
    }

    pub fn embedded_pg_port(&self) -> u16 {
        self.embedded_pg_port.unwrap_or(0)
    }
}
