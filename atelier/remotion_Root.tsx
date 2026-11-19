import React from "react";
import { Composition } from "remotion";
import { GtaVideo, Props } from "./Video";

const defaults: Props = {
  fps: 30, durationInFrames: 60, shots: [], groups: [], items: [], sfx: [], title: null,
  voice: "", music: "", musicStartFrom: 120, musicVolume: 0.16, duck: [],
};

export const Root: React.FC = () => (
  <Composition
    id="GtaVideo"
    component={GtaVideo as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={60}
    defaultProps={defaults}
    calculateMetadata={({ props }) => ({ durationInFrames: (props as Props).durationInFrames, fps: (props as Props).fps })}
  />
);
