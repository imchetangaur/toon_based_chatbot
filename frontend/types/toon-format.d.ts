/**
 * Type declarations for @toon-format/toon
 * In case the package doesn't include its own types
 */

declare module '@toon-format/toon' {
  /**
   * Encode data to TOON format string
   */
  export function encode(data: any): string;

  /**
   * Decode TOON format string to data
   */
  export function decode(toonString: string): any;
}
