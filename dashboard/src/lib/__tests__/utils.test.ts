import { describe, it, expect } from "vitest";
import { formatDuration, formatDate, buildSpanTree, cn } from "../utils";
import type { Span } from "../types";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("handles tailwind conflicts", () => {
    const result = cn("px-4", "px-6");
    expect(result).toBe("px-6");
  });
});

describe("formatDuration", () => {
  it("returns dash for null inputs", () => {
    expect(formatDuration(null, null)).toBe("-");
    expect(formatDuration("2024-01-01T00:00:00Z", null)).toBe("-");
    expect(formatDuration(null, "2024-01-01T00:00:00Z")).toBe("-");
  });

  it("formats milliseconds", () => {
    const result = formatDuration(
      "2024-01-01T00:00:00.000Z",
      "2024-01-01T00:00:00.500Z",
    );
    expect(result).toBe("500ms");
  });

  it("formats seconds", () => {
    const result = formatDuration(
      "2024-01-01T00:00:00Z",
      "2024-01-01T00:00:02Z",
    );
    expect(result).toBe("2.0s");
  });

  it("formats minutes", () => {
    const result = formatDuration(
      "2024-01-01T00:00:00Z",
      "2024-01-01T00:02:00Z",
    );
    expect(result).toBe("2.0m");
  });
});

describe("formatDate", () => {
  it("formats ISO date string", () => {
    const result = formatDate("2024-01-15T12:34:56Z");
    expect(result).toBeTruthy();
    expect(typeof result).toBe("string");
  });
});

describe("buildSpanTree", () => {
  const makeSpan = (id: string, parentId: string | null, name: string): Span => ({
    id,
    trace_id: "t1",
    parent_span_id: parentId,
    name,
    kind: "custom",
    status: "ok",
    input: null,
    output: null,
    metadata: {},
    events: [],
    start_time: "2024-01-01T00:00:00Z",
    end_time: "2024-01-01T00:00:01Z",
    created_at: "2024-01-01T00:00:00Z",
  });

  it("builds flat list as roots", () => {
    const spans = [makeSpan("a", null, "A"), makeSpan("b", null, "B")];
    const tree = buildSpanTree(spans);
    expect(tree).toHaveLength(2);
    expect(tree[0].children).toHaveLength(0);
  });

  it("builds parent-child relationships", () => {
    const spans = [
      makeSpan("parent", null, "Parent"),
      makeSpan("child", "parent", "Child"),
    ];
    const tree = buildSpanTree(spans);
    expect(tree).toHaveLength(1);
    expect(tree[0].span.name).toBe("Parent");
    expect(tree[0].children).toHaveLength(1);
    expect(tree[0].children[0].span.name).toBe("Child");
  });

  it("handles empty array", () => {
    expect(buildSpanTree([])).toHaveLength(0);
  });

  it("orphan spans become roots", () => {
    const spans = [makeSpan("child", "missing-parent", "Orphan")];
    const tree = buildSpanTree(spans);
    expect(tree).toHaveLength(1);
  });
});
