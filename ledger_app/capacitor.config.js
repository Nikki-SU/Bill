module.exports = {
  appId: 'com.ledger.app',
  appName: '账本',
  webDir: 'www',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https',
    cleartext: false
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#f5f5f5',
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#f5f5f5',
      overlaysWebView: true
    }
  }
};
