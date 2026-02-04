import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TraceFilters } from "../trace-filters";

describe("TraceFilters", () => {
  it("renders status dropdown", () => {
    render(<TraceFilters filters={{}} onChange={vi.fn()} />);
    expect(screen.getByLabelText("Status")).toBeDefined();
  });

  it("renders date inputs", () => {
    render(<TraceFilters filters={{}} onChange={vi.fn()} />);
    expect(screen.getByLabelText("Start date")).toBeDefined();
    expect(screen.getByLabelText("End date")).toBeDefined();
  });

  it("calls onChange when status changes", () => {
    const onChange = vi.fn();
    render(<TraceFilters filters={{}} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "ok" } });
    expect(onChange).toHaveBeenCalledWith({ status: "ok" });
  });

  it("calls onChange with empty object when clear is clicked", () => {
    const onChange = vi.fn();
    render(<TraceFilters filters={{ status: "ok" }} onChange={onChange} />);
    fireEvent.click(screen.getByText("Clear filters"));
    expect(onChange).toHaveBeenCalledWith({});
  });

  it("renders current filter values", () => {
    render(<TraceFilters filters={{ status: "error" }} onChange={vi.fn()} />);
    const select = screen.getByLabelText("Status") as HTMLSelectElement;
    expect(select.value).toBe("error");
  });
});
