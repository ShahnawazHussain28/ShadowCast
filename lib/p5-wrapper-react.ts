// @ts-expect-error Upstream package exports an incorrect ESM file name in package.json.
export { P5Canvas } from "../node_modules/@p5-wrapper/react/dist/component/main.esm.js";
export type {
  P5CanvasInstance,
  P5CanvasProps,
  Sketch,
  SketchProps,
} from "../node_modules/@p5-wrapper/react/dist/component/main.d.ts";
