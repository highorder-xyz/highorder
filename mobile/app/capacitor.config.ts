import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'xyz.highorder.mobile.app',
  appName: 'highorder-mobile',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;
