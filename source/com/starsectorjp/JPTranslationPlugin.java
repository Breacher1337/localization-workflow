package com.applicationjp;

import com.fs.legacyapp.api.BasePluginPlugin;
import com.fs.legacyapp.api.Global;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.*;
import java.util.regex.*;

public class JPTranslationPlugin extends BasePluginPlugin {

    public static Map<String, String> TR = new HashMap<>();
    public static List<TranslationPattern> DYNAMIC_TR = new ArrayList<>();

    public static class TranslationPattern {
        public Pattern regex;
        public String replacement;
        public TranslationPattern(String regexStr, String replacement) {
            this.regex = Pattern.compile(regexStr);
            this.replacement = replacement;
        }
    }

    @Override
    public void onApplicationLoad() throws Exception {
        Global.getLogger(this.getClass()).info("Initializing Application JP Translation Plugin (Advanced)...");

        loadStaticTranslations();
        loadDynamicTranslations();

        Global.getLogger(this.getClass()).info("Static and Dynamic JP Translation hooks are active.");
    }

    private void loadStaticTranslations() {
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
            Global.getLogger(this.getClass()).info("Loaded " + TR.size() + " hardcoded UI translations.");
        } catch (Exception e) {
            Global.getLogger(this.getClass()).error("Failed to load hardcoded_ui.csv", e);
        }
    }

    private void loadDynamicTranslations() {
        try {
            JSONArray csvData = Global.getSettings().getMergedSpreadsheetDataForPlugin("original", "data/strings/dynamic_ui.csv", "japanese_localization");
            for (int i = 0; i < csvData.length(); i++) {
                JSONObject row = csvData.getJSONObject(i);
                String regex = row.getString("regex");
                String jap = row.getString("japanese");
                if (regex != null && !regex.isEmpty() && jap != null && !jap.isEmpty()) {
                    // Convert {0} in replacement to $1 for Java Matcher.replaceAll
                    String javaReplacement = jap.replace("{0}", "$1").replace("{1}", "$2").replace("{2}", "$3").replace("{3}", "$4");
                    DYNAMIC_TR.add(new TranslationPattern(regex, javaReplacement));
                }
            }
            Global.getLogger(this.getClass()).info("Loaded " + DYNAMIC_TR.size() + " dynamic UI templates.");
        } catch (Exception e) {
            Global.getLogger(this.getClass()).error("Failed to load dynamic_ui.csv", e);
        }
    }

    public static String translate(String input) {
        if (input == null || input.isEmpty()) return input;

        // 1. Exact match
        if (TR.containsKey(input)) {
            return TR.get(input);
        }

        // 2. Dynamic match
        for (TranslationPattern pt : DYNAMIC_TR) {
            Matcher m = pt.regex.matcher(input);
            if (m.matches()) {
                return m.replaceAll(pt.replacement);
            }
        }

        return input;
    }
}
