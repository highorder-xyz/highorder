use serde::Deserialize;
use clap::Parser;

#[derive(Debug, Clone, Deserialize, Default)]
pub struct Settings {
    pub debug: Option<bool>,
    pub host: Option<String>,
    pub port: Option<u16>,
    pub storage: Option<String>,
    pub db_url: Option<String>,
    pub data_dir: Option<String>,
    pub content_url: Option<String>,
    pub webapp_root: Option<String>,
    pub localdb_data_dir: Option<String>,
    pub localdb_port: Option<u16>,
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
    storage: Option<String>,
    #[arg(long)]
    db_url: Option<String>,
    #[arg(long)]
    data_dir: Option<String>,
    #[arg(long)]
    content_url: Option<String>,
    #[arg(long)]
    webapp_root: Option<String>,
    #[arg(long)]
    localdb_data_dir: Option<String>,
    #[arg(long)]
    localdb_port: Option<u16>,
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
        if let Some(v) = cli.storage { settings.storage = Some(v); }
        if let Some(v) = cli.db_url { settings.db_url = Some(v); }
        if let Some(v) = cli.data_dir { settings.data_dir = Some(v); }
        if let Some(v) = cli.content_url { settings.content_url = Some(v); }
        if let Some(v) = cli.webapp_root { settings.webapp_root = Some(v); }
        if let Some(v) = cli.localdb_data_dir { settings.localdb_data_dir = Some(v); }
        if let Some(v) = cli.localdb_port { settings.localdb_port = Some(v); }

        Ok(settings)
    }

    pub fn debug(&self) -> bool { self.debug.unwrap_or(false) }
    pub fn host(&self) -> String { self.host.clone().unwrap_or_else(|| "0.0.0.0".to_string()) }
    pub fn port(&self) -> u16 { self.port.unwrap_or(9000) }
    pub fn db_url(&self) -> String {
        self.db_url
            .clone()
            .unwrap_or_else(|| "sqlite://./highorder.db?mode=rwc".to_string())
    }

    pub fn storage(&self) -> String {
        if let Some(s) = &self.storage {
            return s.to_lowercase();
        }
        if let Some(u) = &self.db_url {
            let ul = u.to_lowercase();
            if ul.starts_with("sqlite:") {
                if ul.contains(":memory:") { return "memory".to_string(); }
                return "litedb".to_string();
            }
            return "db".to_string();
        }
        "memory".to_string()
    }

    pub fn localdb_data_dir(&self) -> String {
        self.localdb_data_dir
            .clone()
            .unwrap_or_else(|| "./.pg-data".to_string())
    }

    pub fn localdb_port(&self) -> u16 {
        self.localdb_port.unwrap_or(0)
    }
}
