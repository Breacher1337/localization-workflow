import sys

with open(r'.\source\com\applicationjp\JPTranslationPlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = '''package com.applicationjp;

import com.fs.legacyapp.api.BasePluginPlugin;
import com.fs.legacyapp.api.Global;
import org.json.JSONArray;
import org.json.JSONObject;

public class JPTranslationPlugin extends BasePluginPlugin {

    public static java.util.Map<String, String> TR = new java.util.HashMap<>();

    @Override
    public void onApplicationLoad() throws Exception {
        Global.getLogger(this.getClass()).info("Initializing Application JP Translation Plugin...");
        
        try {
            JSONArray csvData = Global.getSettings().getMergedSpreadsheetDataForPlugin("english", "data/strings/hardcoded_ui.csv", "japanese_localization");
            for (int i = 0; i < csvData.length(); i++) {
                JSONObject row = csvData.getJSONObject(i);
                String eng = row.getString("english");
                String jap = row.getString("japanese");
                if (eng != null && !eng.isEmpty() && jap != null && !jap.isEmpty()) {
                    TR.put(eng, jap);
                }
            }
            Global.getLogger(this.getClass()).info("Loaded " + TR.size() + " hardcoded UI translations from CSV.");
        } catch (Exception e) {
            Global.getLogger(this.getClass()).error("Failed to load hardcoded_ui.csv", e);
        }

        Global.getLogger(this.getClass()).info("Static JP Translation hooks are active.");
    }

    @Override
    public void onApplicationLoad(boolean newApplication) {
        Global.getLogger(this.getClass()).info("JP Translation Plugin loaded into application state.");
    }
}
'''

with open(r'.\source\com\applicationjp\JPTranslationPlugin.java', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replaced JPTranslationPlugin.java with dynamic CSV loading logic.")
