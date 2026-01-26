/**
 * TOON Format Parser Utilities
 * Uses official @toon-format/toon library for encoding/decoding
 * Falls back to JSON if library is not available
 */

import { ChatMessage } from '@/types/toon';

// Dynamic import for TOON library with graceful fallback
let toonEncode: ((data: any) => string) | null = null;
let toonDecode: ((str: string) => any) | null = null;

// Initialize TOON functions (will run on client-side)
if (typeof window !== 'undefined') {
  try {
    // Use dynamic import for client-side only
    import('@toon-format/toon')
      .then((toonModule) => {
        toonEncode = toonModule.encode;
        toonDecode = toonModule.decode;
        console.log('✅ @toon-format/toon library loaded');
      })
      .catch((error) => {
        console.warn('⚠️ @toon-format/toon not available, using JSON fallback');
        toonEncode = (data: any) => JSON.stringify(data);
        toonDecode = (str: string) => JSON.parse(str);
      });
  } catch (error) {
    console.warn('⚠️ Error loading @toon-format/toon, using JSON fallback');
  }
}

// Ensure fallback functions are always available
const encode = (data: any): string => {
  if (toonEncode) {
    try {
      return toonEncode(data);
    } catch (error) {
      console.error('Error encoding with TOON:', error);
      return JSON.stringify(data);
    }
  }
  // Fallback to JSON
  return JSON.stringify(data);
};

const decode = (str: string): any => {
  if (toonDecode) {
    try {
      return toonDecode(str);
    } catch (error) {
      console.error('Error decoding with TOON:', error);
      return JSON.parse(str);
    }
  }
  // Fallback to JSON
  return JSON.parse(str);
};

/**
 * Encode messages to TOON format
 */
export function encodeToon(messages: ChatMessage[]): string {
  if (messages.length === 0) return '[]';

  try {
    return encode(messages);
  } catch (error) {
    console.error('Error encoding to TOON:', error);
    return JSON.stringify(messages);
  }
}

/**
 * Decode TOON format to messages
 */
export function decodeToon(toonString: string): ChatMessage[] {
  if (!toonString || toonString.trim() === '') return [];

  try {
    const decoded = decode(toonString);

    // Ensure it's an array
    if (Array.isArray(decoded)) {
      return decoded as ChatMessage[];
    }

    // If it's an object with a messages property
    if (decoded && typeof decoded === 'object' && 'messages' in decoded) {
      return (decoded as any).messages as ChatMessage[];
    }

    // Single object, wrap in array
    if (decoded && typeof decoded === 'object') {
      return [decoded] as ChatMessage[];
    }

    return [];
  } catch (error) {
    console.error('Error decoding TOON:', error);

    // Fallback: try JSON parse
    try {
      const parsed = JSON.parse(toonString);
      return Array.isArray(parsed) ? parsed : [parsed];
    } catch {
      return [];
    }
  }
}

/**
 * Decode a single TOON response object
 */
export function decodeToonResponse(toonString: string): { role: string; content: string } | null {
  if (!toonString) return null;

  try {
    const decoded = decode(toonString);

    // Check if it's a valid response object
    if (decoded && typeof decoded === 'object' && 'role' in decoded && 'content' in decoded) {
      return decoded as { role: string; content: string };
    }

    return null;
  } catch (error) {
    console.error('Error decoding TOON response:', error);

    // Fallback to JSON
    try {
      return JSON.parse(toonString);
    } catch {
      return null;
    }
  }
}

/**
 * Encode any data to TOON format
 */
export function encodeToToon(data: any): string {
  try {
    return encode(data);
  } catch (error) {
    console.error('Error encoding to TOON:', error);
    return JSON.stringify(data);
  }
}

/**
 * Decode any TOON string to data
 */
export function decodeFromToon(toonString: string): any {
  try {
    return decode(toonString);
  } catch (error) {
    console.error('Error decoding from TOON:', error);
    try {
      return JSON.parse(toonString);
    } catch {
      return null;
    }
  }
}

/**
 * Format content for display
 */
export function formatContent(content: string): string {
  if (!content) return '';
  return content.trim();
}
