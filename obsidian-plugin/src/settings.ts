import { App, PluginSettingTab, Setting } from "obsidian";
import type DeepNotesPlugin from "./main";

export interface DeepNotesSettings {
  backendUrl: string;
  apiKey: string;
}

export const DEFAULT_SETTINGS: DeepNotesSettings = {
  backendUrl: "http://localhost:8000",
  apiKey: "",
};

export class DeepNotesSettingTab extends PluginSettingTab {
  plugin: DeepNotesPlugin;

  constructor(app: App, plugin: DeepNotesPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    new Setting(containerEl)
      .setName("Backend URL")
      .setDesc("URL of the Deep Notes FastAPI server")
      .addText((text) =>
        text
          .setPlaceholder("http://localhost:8000")
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (value) => {
            this.plugin.settings.backendUrl = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("API Key")
      .setDesc("API key for authenticating with the backend")
      .addText((text) =>
        text
          .setPlaceholder("your-api-key")
          .setValue(this.plugin.settings.apiKey)
          .onChange(async (value) => {
            this.plugin.settings.apiKey = value;
            await this.plugin.saveSettings();
          })
      );
  }
}
