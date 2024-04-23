package xyz.highorder.mobile.app;

import com.getcapacitor.BridgeActivity;
public class MainActivity extends BridgeActivity {


    @Override
    protected void load() {
        super.load();
        this.adjustFontScale();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        Log.i("PLUGIN", "regster plugin...");
        super.onCreate(savedInstanceState);
    }

    public void adjustFontScale() {
        // https://github.com/ionic-team/capacitor/discussions/3335
        WebSettings settings = bridge.getWebView().getSettings();
        settings.setTextZoom(100);
        settings.setSupportZoom(false);
    }

}