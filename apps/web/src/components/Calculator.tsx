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
      const result = evaluate(expression);
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
        <button onClick={() => insertSymbol("factorial(")}>n!</button>
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
          placeholder="e.g., exp(-5) * 5^3 / factorial(3)"
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
