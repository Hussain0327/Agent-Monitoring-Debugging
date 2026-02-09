import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "../status-badge";

describe("StatusBadge", () => {
  it("renders the status text", () => {
    render(<StatusBadge status="ok" />);
    expect(screen.getByText("ok")).toBeTruthy();
  });

  it("has status role", () => {
    render(<StatusBadge status="ok" />);
    expect(screen.getByRole("status")).toBeTruthy();
  });

  it("has aria-label", () => {
    render(<StatusBadge status="error" />);
    const badge = screen.getByRole("status");
    expect(badge.getAttribute("aria-label")).toBe("Status: error");
  });

  it("applies success styles for ok status", () => {
    render(<StatusBadge status="ok" />);
    const badge = screen.getByRole("status");
    expect(badge.className).toContain("success");
  });

  it("applies danger styles for error status", () => {
    render(<StatusBadge status="error" />);
    const badge = screen.getByRole("status");
    expect(badge.className).toContain("danger");
  });

  it("applies muted styles for unknown status", () => {
    render(<StatusBadge status="unknown_thing" />);
    const badge = screen.getByRole("status");
    expect(badge.className).toContain("muted-foreground");
  });

  it("supports sm size", () => {
    render(<StatusBadge status="ok" size="sm" />);
    const badge = screen.getByRole("status");
    expect(badge.className).toContain("text-[10px]");
  });

  it("defaults to md size", () => {
    render(<StatusBadge status="ok" />);
    const badge = screen.getByRole("status");
    expect(badge.className).toContain("text-[11px]");
  });
});
