import { fetchFromApi } from "../utils/api";

// Interface for theme API responses

export interface ThemeResponse {
  status: string;
  theme: "light" | "dark";
  message?: string;
}

/**
 * Get the current theme mode from the API
 * @returns Promise with the current theme mode
 */
export async function getCurrentTheme(): Promise<"light" | "dark"> {
  try {
    const response = await fetchFromApi("/theme");
    return response.theme;
  } catch (error) {
    console.error("Error fetching theme:", error);
    return "light"; // Default to light theme if there's an error
  }
}

/**
 * Set the theme mode via the API
 * @param mode The theme mode to set ("light" or "dark")
 * @returns Promise with the updated theme mode
 */
export async function setThemeMode(mode: "light" | "dark"): Promise<"light" | "dark"> {
  try {
    const response = await fetchFromApi("/theme", {
      method: "POST",
      body: JSON.stringify({ mode })
    });
    return response.theme;
  } catch (error) {
    console.error("Error setting theme:", error);
    return mode; // Return the requested mode even if there's an error
  }
}
