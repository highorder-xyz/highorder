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
}
