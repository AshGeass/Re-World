"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { api, TimelineEvent } from "@/lib/api";
import { useAppContext } from "./AppProvider";

export default function TimelineViz() {
  const { storyId, branchId, currentSequence, setCurrentSequence } = useAppContext();
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  
  useEffect(() => {
    if (storyId) {
      api.getTimeline(storyId, branchId).then(data => {
        setEvents(data.events);
      });
    }
  }, [storyId, branchId]);

  useEffect(() => {
    if (!events.length || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    
    // Clear previous
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    const margin = { top: 40, right: 40, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    
    // Create scales
    const xScale = d3.scaleLinear()
      .domain([0, d3.max(events, d => d.sequence) || 10])
      .range([0, innerWidth]);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left}, ${height / 2})`);

    // Draw main timeline axis
    g.append("line")
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", innerWidth)
      .attr("y2", 0)
      .attr("stroke", "var(--border)")
      .attr("stroke-width", 2);

    // Knowledge horizon (current sequence)
    const horizonX = xScale(currentSequence);
    
    // Draw horizon indicator
    const horizonGroup = g.append("g")
      .attr("class", "horizon")
      .attr("transform", `translate(${horizonX}, 0)`);
      
    horizonGroup.append("line")
      .attr("y1", -height/2)
      .attr("y2", height/2)
      .attr("stroke", "var(--primary-muted)")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "4 4");
      
    horizonGroup.append("text")
      .attr("y", -height/2 + 20)
      .attr("x", 5)
      .attr("fill", "var(--primary-muted)")
      .attr("font-family", "monospace")
      .attr("font-size", "10px")
      .text("KNOWLEDGE HORIZON");

    // Draw events
    const nodes = g.selectAll(".event-node")
      .data(events)
      .enter()
      .append("g")
      .attr("class", "event-node")
      .attr("transform", d => `translate(${xScale(d.sequence)}, 0)`)
      .style("cursor", "pointer")
      .on("click", (e, d) => {
        setCurrentSequence(d.sequence);
      });

    // Event circles
    nodes.append("circle")
      .attr("r", 8)
      .attr("fill", d => d.canonical ? "var(--canon)" : "var(--generated)")
      .attr("stroke", "var(--background)")
      .attr("stroke-width", 2)
      .attr("opacity", d => d.sequence > currentSequence ? 0.3 : 1);

    // Event labels
    nodes.append("text")
      .attr("y", (d, i) => i % 2 === 0 ? -20 : 30)
      .attr("text-anchor", "middle")
      .attr("fill", d => d.sequence > currentSequence ? "var(--border)" : "var(--primary)")
      .attr("font-family", "serif")
      .attr("font-size", "12px")
      .text(d => d.title.length > 20 ? d.title.substring(0, 20) + '...' : d.title);

  }, [events, currentSequence, setCurrentSequence]);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-background relative group">
      <div className="absolute top-4 left-4 z-10 flex gap-4 text-xs font-mono">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-canon" /> Canon
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-generated" /> Generated
        </div>
      </div>
      <div ref={containerRef} className="flex-1 w-full h-full">
        <svg ref={svgRef} className="w-full h-full" />
      </div>
    </div>
  );
}
