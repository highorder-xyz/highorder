use serde::Deserialize;
use clap::Parser;

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

#[derive(Debug, Clone, Parser)]
#[command(name = "highorder")] 
struct CliArgs {
    #[arg(long)]
    debug: Option<bool>,
    #[arg(long)]
    host: Option<String>,
    #[arg(long)]
    port: Option<u16>,
    #[arg(long)]
    run_editor: Option<bool>,
    #[arg(long)]
    db_url: Option<String>,
    #[arg(long)]
    data_dir: Option<String>,
    #[arg(long)]
    content_url: Option<String>,
    #[arg(long)]
    webapp_root: Option<String>,
    #[arg(long)]
    use_embedded_postgres: Option<bool>,
    #[arg(long)]
    embedded_pg_data_dir: Option<String>,
    #[arg(long)]
    embedded_pg_port: Option<u16>,
}

impl Settings {
    pub fn load() -> anyhow::Result<Self> {
        let cli = CliArgs::parse();
        let mut builder = config::Config::builder();
        builder = builder.add_source(config::File::with_name("settings").required(false));
        builder = builder.add_source(config::Environment::with_prefix("HIGHORDER").separator("__"));
        let cfg = builder.build()?;
        let mut settings: Settings = cfg.try_deserialize()?;

        if let Some(v) = cli.debug { settings.debug = Some(v); }
        if let Some(v) = cli.host { settings.host = Some(v); }
        if let Some(v) = cli.port { settings.port = Some(v); }
        if let Some(v) = cli.run_editor { settings.run_editor = Some(v); }
        if let Some(v) = cli.db_url { settings.db_url = Some(v); }
        if let Some(v) = cli.data_dir { settings.data_dir = Some(v); }
        if let Some(v) = cli.content_url { settings.content_url = Some(v); }
        if let Some(v) = cli.webapp_root { settings.webapp_root = Some(v); }
        if let Some(v) = cli.use_embedded_postgres { settings.use_embedded_postgres = Some(v); }
        if let Some(v) = cli.embedded_pg_data_dir { settings.embedded_pg_data_dir = Some(v); }
        if let Some(v) = cli.embedded_pg_port { settings.embedded_pg_port = Some(v); }

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
