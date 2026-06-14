import { useState, useRef, useEffect } from "react";
import { evaluate } from "mathjs";

interface CalculatorProps {
  onUseResult?: (result: string) => void;
}

interface HistoryEntry {
  expression: string;
  result: string;
  isError: boolean;
}

export default function Calculator({ onUseResult }: CalculatorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [expression, setExpression] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  const preprocessExpression = (rawExpression: string) => {
    let nextExpression = rawExpression;
    const factorialTarget = /((?:\d+(?:\.\d+)?)|(?:[A-Za-z_]\w*)|(?:\([^()]+\)))!/g;

    while (factorialTarget.test(nextExpression)) {
      nextExpression = nextExpression.replace(
        factorialTarget,
        "factorial($1)",
      );
    }

    return nextExpression;
  };

  const nCr = (n: number, r: number) => {
    if (!Number.isInteger(n) || !Number.isInteger(r)) {
      throw new Error("nCr only supports integers");
    }
    if (n < 0 || r < 0 || r > n) {
      throw new Error("nCr requires n ≥ r ≥ 0");
    }
    const choose = Math.min(r, n - r);
    let result = 1;
    for (let i = 1; i <= choose; i += 1) {
      result = (result * (n - choose + i)) / i;
    }
    return result;
  };

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [history]);

  const handleEvaluate = () => {
    if (!expression.trim()) return;

    try {
      const normalizedExpression = preprocessExpression(expression);
      const result = evaluate(normalizedExpression, { nCr });
      const formatted =
        typeof result === "number"
          ? Number(result.toPrecision(8)).toString()
          : String(result);

      setHistory([
        ...history,
        { expression, result: formatted, isError: false },
      ]);
      setExpression("");
    } catch (err: any) {
      setHistory([
        ...history,
        {
          expression,
          result: err.message || "Error",
          isError: true,
        },
      ]);
      setExpression("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleEvaluate();
    }
    if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  const handleUseResult = (result: string) => {
    if (onUseResult && !result.includes("Error")) {
      onUseResult(result);
    }
  };

  const insertSymbol = (symbol: string) => {
    setExpression((prev) => prev + symbol);
    inputRef.current?.focus();
  };

  if (!isOpen) {
    return (
      <button
        className="calc-toggle-btn"
        onClick={() => setIsOpen(true)}
        title="Open calculator"
      >
        🧮
      </button>
    );
  }

  return (
    <div className="calculator-panel">
      <div className="calc-header">
        <span>Calculator</span>
        <button className="calc-close-btn" onClick={() => setIsOpen(false)}>
          ×
        </button>
      </div>

      {history.length > 0 && (
        <div className="calc-history" ref={historyRef}>
          {history.map((entry, i) => (
            <div
              key={i}
              className={`calc-entry ${entry.isError ? "error" : ""}`}
            >
              <div className="calc-expr">{entry.expression}</div>
              <div
                className="calc-result"
                onClick={() => handleUseResult(entry.result)}
                title={entry.isError ? undefined : "Click to use this result"}
              >
                = {entry.result}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="calc-symbols">
        <button onClick={() => insertSymbol("^")}>x^y</button>
        <button onClick={() => insertSymbol("sqrt(")}>√</button>
        <button onClick={() => insertSymbol("!")}>n!</button>
        <button onClick={() => insertSymbol("nCr(")}>nCr</button>
        <button onClick={() => insertSymbol("exp(")}>e^x</button>
        <button onClick={() => insertSymbol("log(")}>ln</button>
        <button onClick={() => insertSymbol("(")}>(</button>
        <button onClick={() => insertSymbol(")")}>)</button>
        <button onClick={() => insertSymbol(" / ")}>/</button>
        <button onClick={() => insertSymbol(" * ")}>×</button>
      </div>

      <div className="calc-input-row">
        <input
          ref={inputRef}
          type="text"
          className="calc-input"
          value={expression}
          onChange={(e) => setExpression(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., 5! / (2! * 3!) or nCr(5,2)"
        />
        <button className="calc-eval-btn" onClick={handleEvaluate}>
          =
        </button>
      </div>

      <div className="calc-hint">
        Enter to calculate • Click result to use as answer
      </div>
    </div>
  );
}
