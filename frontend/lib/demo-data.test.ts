import { describe, expect, it } from "vitest";
import { etfs, formatAum, similarity } from "./demo-data";

describe("deterministic demo analytics", () => {
  it("formats AUM without fabricating missing values", () => {
    expect(formatAum(12840, "EUR")).toBe("€12.8B");
    expect(formatAum(null, "EUR")).toBe("Not available");
  });

  it("returns explainable bounded similarity", () => {
    const result = similarity(etfs[0], etfs[3]);
    expect(result.score).toBeGreaterThan(0);
    expect(result.score).toBeLessThanOrEqual(100);
    expect(result.contributions.reduce((sum, item) => sum + item.points, 0)).toBeCloseTo(result.score);
    expect(result.contributions[0]).toHaveProperty("label");
  });
});
