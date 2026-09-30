declare module 'node:test' { const test: (name: string, fn: () => void | Promise<void>) => void; export default test; }
declare module 'node:assert/strict' {
  const assert: {
    equal(actual: unknown, expected: unknown, message?: string): void;
    notEqual(actual: unknown, expected: unknown, message?: string): void;
    deepEqual(actual: unknown, expected: unknown, message?: string): void;
    ok(value: unknown, message?: string): asserts value;
    match(actual: string, regexp: RegExp, message?: string): void;
    throws(block: () => unknown, error?: RegExp, message?: string): void;
  };
  export default assert;
}
declare module 'node:fs' {
  export function readFileSync(path: string, encoding: 'utf8'): string;
}
