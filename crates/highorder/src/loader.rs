use serde::Deserialize;
use serde_json::Value;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Deserialize, Default)]
pub struct ApplicationClientKey {
    pub app_id: String,
    pub client_key: String,
    pub client_secret: String,
    pub valid: bool,
}

#[derive(Debug, Clone, Deserialize, Default)]
pub struct ApplicationSummary {
    pub app_id: String,
    pub app_name: String,
    #[serde(default)]
    pub client_keys: Vec<ApplicationClientKey>,
}

pub struct ApplicationFolder;

impl ApplicationFolder {
    pub fn get_app_root(app_id: &str, data_dir: &Path) -> PathBuf {
        data_dir.join(format!("APP_{}", app_id))
    }
}

fn read_to_string(path: &Path) -> std::io::Result<String> {
    let mut f = File::open(path)?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

fn read_zip_entry(zip_path: &Path, entry_path: &str) -> anyhow::Result<Option<String>> {
    let file = File::open(zip_path)?;
    let mut zip = zip::ZipArchive::new(file)?;
    if let Ok(mut f) = zip.by_name(entry_path) {
        let mut s = String::new();
        f.read_to_string(&mut s)?;
        return Ok(Some(s));
    }
    Ok(None)
}

pub async fn load_app_summary(app_id: &str, data_dir: &Path) -> anyhow::Result<Option<ApplicationSummary>> {
    // Try release.json first
    let app_root = ApplicationFolder::get_app_root(app_id, data_dir);
    let release_path = app_root.join("release.json");
    if release_path.exists() {
        let content = read_to_string(&release_path)?;
        let v: Value = serde_json::from_str(&content)?;
        if let Some(current) = v.get("current").and_then(|x| x.as_str()) {
            let zip_name = format!("APP_{}_{}.zip", app_id, current);
            let zip_path = app_root.join(zip_name);
            if zip_path.exists() {
                if let Some(s) = read_zip_entry(&zip_path, "app/app.json")? {
                    let summary: ApplicationSummary = serde_json::from_str(&s)?;
                    return Ok(Some(summary));
                }
            }
        }
    }
    // Fallback to raw file
    let app_json = ApplicationFolder::get_app_root(app_id, data_dir).join("app/app.json");
    if app_json.exists() {
        let content = read_to_string(&app_json)?;
        let summary: ApplicationSummary = serde_json::from_str(&content)?;
        return Ok(Some(summary));
    }
    Ok(None)
}
