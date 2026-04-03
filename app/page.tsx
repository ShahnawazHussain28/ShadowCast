"use client";
import dynamic from "next/dynamic";
import type { ComponentType } from "react";
import { type P5CanvasProps, type Sketch } from "@/lib/p5-wrapper-react";

const P5Canvas = dynamic(
  () => import("@/lib/p5-wrapper-react").then((module) => module.P5Canvas),
  { ssr: false },
) as ComponentType<P5CanvasProps>;

const sketch: Sketch = (p5) => {
  p5.setup = () => p5.createCanvas(600, 400, p5.WEBGL);

  p5.draw = () => {
    p5.background(250);
    p5.normalMaterial();
    p5.push();
    p5.rotateZ(p5.frameCount * 0.01);
    p5.rotateX(p5.frameCount * 0.01);
    p5.rotateY(p5.frameCount * 0.01);
    p5.plane(100);
    p5.pop();
  };
};

export default function Page() {
  return <P5Canvas sketch={sketch} />;
}
