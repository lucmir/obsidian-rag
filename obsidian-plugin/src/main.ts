import { Plugin } from "obsidian";
import { ApiClient } from "./api-client";
import { DeepNotesSettings, DEFAULT_SETTINGS, DeepNotesSettingTab } from "./settings";
import { DeepNotesSearchView, VIEW_TYPE } from "./search-view";

export default class DeepNotesPlugin extends Plugin {
  settings!: DeepNotesSettings;
  apiClient!: ApiClient;

  async onload(): Promise<void> {
    await this.loadSettings();

    this.apiClient = new ApiClient(
      this.settings.backendUrl,
      this.settings.apiKey
    );

    this.registerView(VIEW_TYPE, (leaf) => new DeepNotesSearchView(leaf, this));

    this.addRibbonIcon("bot", "Deep Notes: Search", () => {
      this.activateView();
    });

    this.addCommand({
      id: "open-search",
      name: "Search",
      callback: () => this.activateView(),
    });

    this.addSettingTab(new DeepNotesSettingTab(this.app, this));

    this.addStatusBarItem().setText("Deep Notes");
  }

  onunload(): void {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE);
  }

  async loadSettings(): Promise<void> {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
    this.apiClient.updateConfig(
      this.settings.backendUrl,
      this.settings.apiKey
    );
  }

  private async activateView(): Promise<void> {
    const existing = this.app.workspace.getLeavesOfType(VIEW_TYPE);
    if (existing.length > 0) {
      this.app.workspace.revealLeaf(existing[0]);
      return;
    }
    const leaf = this.app.workspace.getRightLeaf(false);
    if (leaf) {
      await leaf.setViewState({ type: VIEW_TYPE, active: true });
      this.app.workspace.revealLeaf(leaf);
    }
  }
}
