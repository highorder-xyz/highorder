"""
PostgreSQL binary downloader and installer
"""

import os
import shutil
import tarfile
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm

from .config import PostgreSQLConfig
from .exceptions import PostgreSQLInstallError


class PostgreSQLDownloader:
    """Handles downloading and installing PostgreSQL binaries"""
    
    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        
    def is_installed(self) -> bool:
        """Check if PostgreSQL is already installed for the current version"""
        extracted_dir = self._get_extracted_dir_name()
        pg_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "postgres"
        if os.name == 'nt':
            pg_bin = pg_bin.with_suffix('.exe')
        return pg_bin.exists()
    
    def _get_extracted_dir_name(self) -> str:
        """Get the expected extracted directory name"""
        platform_map = {
            "linux-amd64": "x86_64-unknown-linux-gnu",
            "linux-arm64": "aarch64-unknown-linux-gnu", 
            "darwin-amd64": "x86_64-apple-darwin",
            "darwin-arm64": "aarch64-apple-darwin",
            "windows-amd64": "x86_64-pc-windows-msvc"
        }
        target = platform_map.get(self.config.platform)
        return f"postgresql-{self.config.version}.0-{target}"
    
    def download_and_install(self) -> None:
        """Download and install PostgreSQL binaries"""
        if self.is_installed():
            print(f"PostgreSQL {self.config.version} already installed, skipping download.")
            return
            
        try:
            # Create install directory
            os.makedirs(self.config.install_dir, exist_ok=True)
            
            # Download PostgreSQL archive
            download_url = self.config.get_download_url()
            archive_path = self._download_archive(download_url)
            
            # Extract archive
            self._extract_archive(archive_path)
            
            # Cleanup downloaded archive
            os.unlink(archive_path)
            
        except Exception as e:
            raise PostgreSQLInstallError(f"Failed to install PostgreSQL: {e}")
    
    def _download_archive(self, url: str) -> str:
        """Download PostgreSQL archive with progress bar"""
        filename = url.split('/')[-1]
        archive_path = os.path.join(tempfile.gettempdir(), filename)
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(archive_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {filename}") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            return archive_path
            
        except requests.RequestException as e:
            raise PostgreSQLInstallError(f"Failed to download PostgreSQL: {e}")
    
    def _extract_archive(self, archive_path: str) -> None:
        """Extract PostgreSQL archive to install directory"""
        try:
            if archive_path.endswith('.tar.gz'):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(self.config.install_dir)
            elif archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.config.install_dir)
            else:
                raise PostgreSQLInstallError(f"Unsupported archive format: {archive_path}")
                
        except Exception as e:
            raise PostgreSQLInstallError(f"Failed to extract PostgreSQL archive: {e}")
    
    def get_postgres_bin_path(self) -> Path:
        """Get path to postgres binary"""
        extracted_dir = self._get_extracted_dir_name()
        pg_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "postgres"
        if os.name == 'nt':
            pg_bin = pg_bin.with_suffix('.exe')
        return pg_bin
    
    def get_initdb_bin_path(self) -> Path:
        """Get path to initdb binary"""
        extracted_dir = self._get_extracted_dir_name()
        initdb_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "initdb"
        if os.name == 'nt':
            initdb_bin = initdb_bin.with_suffix('.exe')
        return initdb_bin
    
    def get_psql_bin_path(self) -> Path:
        """Get path to psql binary"""
        extracted_dir = self._get_extracted_dir_name()
        psql_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "psql"
        if os.name == 'nt':
            psql_bin = psql_bin.with_suffix('.exe')
        return psql_bin
    
    def get_createdb_bin_path(self) -> Path:
        """Get path to createdb binary"""
        extracted_dir = self._get_extracted_dir_name()
        createdb_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "createdb"
        if os.name == 'nt':
            createdb_bin = createdb_bin.with_suffix('.exe')
        return createdb_bin
    
    def get_dropdb_bin_path(self) -> Path:
        """Get path to dropdb binary"""
        extracted_dir = self._get_extracted_dir_name()
        dropdb_bin = Path(self.config.install_dir) / extracted_dir / "bin" / "dropdb"
        if os.name == 'nt':
            dropdb_bin = dropdb_bin.with_suffix('.exe')
        return dropdb_bin
