/**
 * Utility function for combining class names with Tailwind CSS.
 * Uses clsx for conditional classes and tailwind-merge for deduplication.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines class names and merges Tailwind CSS classes intelligently.
 * 
 * @param inputs - Class names, objects, or arrays of class names
 * @returns Merged class name string
 * 
 * @example
 * cn('px-2 py-1', 'px-4') // Returns 'py-1 px-4' (px-2 is overridden)
 * cn('text-red-500', { 'text-blue-500': isBlue }) // Conditional classes
 * cn(['bg-white', 'text-black'], 'hover:bg-gray-100') // Array support
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Creates a variant-based class name generator.
 * Useful for component variants with consistent styling patterns.
 * 
 * @param base - Base classes that are always applied
 * @param variants - Object mapping variant names to class strings
 * @param defaultVariant - Default variant to use
 * @returns Function that generates class names based on variant
 * 
 * @example
 * const buttonVariants = createVariants(
 *   'px-4 py-2 rounded font-medium',
 *   {
 *     primary: 'bg-blue-500 text-white hover:bg-blue-600',
 *     secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
 *     danger: 'bg-red-500 text-white hover:bg-red-600'
 *   },
 *   'primary'
 * );
 * 
 * buttonVariants('secondary') // Returns combined classes for secondary variant
 */
export function createVariants<T extends Record<string, string>>(
  base: string,
  variants: T,
  defaultVariant: keyof T
) {
  return (variant: keyof T = defaultVariant, additionalClasses?: string) => {
    return cn(base, variants[variant], additionalClasses);
  };
}

/**
 * Conditionally applies classes based on a boolean condition.
 * 
 * @param condition - Boolean condition
 * @param trueClasses - Classes to apply when condition is true
 * @param falseClasses - Classes to apply when condition is false
 * @returns Appropriate class string
 * 
 * @example
 * conditionalClasses(isActive, 'bg-blue-500 text-white', 'bg-gray-200 text-gray-700')
 */
export function conditionalClasses(
  condition: boolean,
  trueClasses: string,
  falseClasses: string = ''
): string {
  return condition ? trueClasses : falseClasses;
}

/**
 * Generates responsive class names for different screen sizes.
 * 
 * @param classes - Object mapping breakpoints to class names
 * @returns Combined responsive class string
 * 
 * @example
 * responsive({
 *   base: 'text-sm',
 *   sm: 'text-base',
 *   md: 'text-lg',
 *   lg: 'text-xl'
 * }) // Returns 'text-sm sm:text-base md:text-lg lg:text-xl'
 */
export function responsive(classes: {
  base?: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  '2xl'?: string;
}): string {
  const { base, sm, md, lg, xl, '2xl': xl2 } = classes;
  
  return cn(
    base,
    sm && `sm:${sm}`,
    md && `md:${md}`,
    lg && `lg:${lg}`,
    xl && `xl:${xl}`,
    xl2 && `2xl:${xl2}`
  );
}

/**
 * Generates focus ring classes for accessibility.
 * 
 * @param color - Focus ring color (default: 'blue')
 * @param offset - Focus ring offset (default: '2')
 * @returns Focus ring class string
 * 
 * @example
 * focusRing() // Returns 'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
 * focusRing('red', '1') // Returns 'focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1'
 */
export function focusRing(color: string = 'blue', offset: string = '2'): string {
  return cn(
    'focus:outline-none',
    'focus:ring-2',
    `focus:ring-${color}-500`,
    `focus:ring-offset-${offset}`
  );
}

/**
 * Common animation classes for transitions.
 */
export const animations = {
  fadeIn: 'animate-in fade-in duration-200',
  fadeOut: 'animate-out fade-out duration-200',
  slideIn: 'animate-in slide-in-from-bottom-4 duration-300',
  slideOut: 'animate-out slide-out-to-bottom-4 duration-300',
  scaleIn: 'animate-in zoom-in-95 duration-200',
  scaleOut: 'animate-out zoom-out-95 duration-200',
  spin: 'animate-spin',
  pulse: 'animate-pulse',
  bounce: 'animate-bounce',
} as const;

/**
 * Common shadow classes.
 */
export const shadows = {
  sm: 'shadow-sm',
  base: 'shadow',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  '2xl': 'shadow-2xl',
  inner: 'shadow-inner',
  none: 'shadow-none',
} as const;

/**
 * Common border radius classes.
 */
export const rounded = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  base: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  '3xl': 'rounded-3xl',
  full: 'rounded-full',
} as const;
