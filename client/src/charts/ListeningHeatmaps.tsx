import { Text } from "@mantine/core";
import { Fragment } from "react";

import {
  HourByWeekdayHeatmapCell,
  MonthByYearHeatmapCell,
  WeekdayByWeekHeatmapCell,
} from "../api";
import styles from "./ListeningHeatmaps.module.css";

const weekdays = [
  { value: 1, label: "Mon" },
  { value: 2, label: "Tue" },
  { value: 3, label: "Wed" },
  { value: 4, label: "Thu" },
  { value: 5, label: "Fri" },
  { value: 6, label: "Sat" },
  { value: 7, label: "Sun" },
];

const months = [
  { value: 1, label: "Jan" },
  { value: 2, label: "Feb" },
  { value: 3, label: "Mar" },
  { value: 4, label: "Apr" },
  { value: 5, label: "May" },
  { value: 6, label: "Jun" },
  { value: 7, label: "Jul" },
  { value: 8, label: "Aug" },
  { value: 9, label: "Sep" },
  { value: 10, label: "Oct" },
  { value: 11, label: "Nov" },
  { value: 12, label: "Dec" },
];

interface HeatmapRow {
  key: string;
  label: string;
}

interface HeatmapColumn {
  key: string;
  label: string;
}

interface HeatmapProps {
  title: string;
  description: string;
  rows: HeatmapRow[];
  columns: HeatmapColumn[];
  values: Map<string, number>;
  cellHeight?: number;
  cellWidth?: number;
}

function cellKey(rowKey: string, columnKey: string) {
  return `${rowKey}:${columnKey}`;
}

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function parseDateKey(dateKey: string): Date {
  return new Date(`${dateKey}T00:00:00Z`);
}

function addDays(date: Date, days: number): Date {
  const next = new Date(date.getTime());
  next.setUTCDate(date.getUTCDate() + days);
  return next;
}

function addWeeks(date: Date, weeks: number): Date {
  return addDays(date, weeks * 7);
}

function heatColor(value: number, maxValue: number): string {
  if (maxValue <= 0 || value <= 0) return "rgb(0, 0, 0)";
  const intensity = Math.sqrt(value / maxValue);
  const red = Math.round(34 * intensity);
  const green = Math.round(139 * intensity);
  const blue = Math.round(34 * intensity);
  return `rgb(${red}, ${green}, ${blue})`;
}

function Heatmap({
  title,
  description,
  rows,
  columns,
  values,
  cellHeight = 18,
  cellWidth = 16,
}: HeatmapProps) {
  if (values.size === 0) return null;

  const maxValue = Math.max(...values.values());
  const gridTemplateColumns = `3rem repeat(${columns.length}, minmax(${cellWidth}px, 1fr))`;

  return (
    <section className={styles.heatmap}>
      <h3>{title}</h3>
      <Text c="dimmed" className={styles.description}>
        {description}
      </Text>
      <div className={styles.scroll}>
        <div className={styles.grid} style={{ gridTemplateColumns }}>
          <div />
          {columns.map((column) => (
            <div key={column.key} className={styles.columnLabel}>
              {column.label}
            </div>
          ))}
          {rows.map((row) => (
            <Fragment key={row.key}>
              <div key={`${row.key}:label`} className={styles.rowLabel}>
                {row.label}
              </div>
              {columns.map((column) => {
                const value = values.get(cellKey(row.key, column.key)) ?? 0;
                return (
                  <div
                    key={cellKey(row.key, column.key)}
                    aria-label={`${row.label}, ${column.label || column.key}: ${value} streams`}
                    className={styles.cell}
                    style={{
                      backgroundColor: heatColor(value, maxValue),
                      height: cellHeight,
                    }}
                    title={`${row.label}, ${column.label || column.key}: ${value} streams`}
                  />
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
      <div className={styles.legend}>
        <span>Fewer streams</span>
        <span className={styles.legendGradient} />
        <span>More streams</span>
      </div>
    </section>
  );
}

export function WeekdayByWeekHeatmap({
  values,
}: {
  values: WeekdayByWeekHeatmapCell[];
}) {
  if (values.length === 0) return null;

  const weekStarts = values.map((value) => parseDateKey(value.week_start));
  const minWeek = new Date(Math.min(...weekStarts.map((date) => date.getTime())));
  const maxWeek = new Date(Math.max(...weekStarts.map((date) => date.getTime())));
  const columns: HeatmapColumn[] = [];

  for (let week = minWeek; week <= maxWeek; week = addWeeks(week, 1)) {
    const key = formatDate(week);
    const isFirstWeekOfYear = week.getUTCMonth() === 0 && week.getUTCDate() <= 7;
    columns.push({
      key,
      label: isFirstWeekOfYear ? `${week.getUTCFullYear()}` : "",
    });
  }

  const heatmapValues = new Map(
    values.map((value) => [
      cellKey(`${value.day_of_week}`, value.week_start),
      value.stream_count,
    ])
  );

  return (
    <Heatmap
      title="Streams by weekday and week"
      description="Each column is one week in your listening history. Darker cells show heavier listening on that day of the week."
      rows={weekdays.map((day) => ({ key: `${day.value}`, label: day.label }))}
      columns={columns}
      values={heatmapValues}
      cellHeight={13}
      cellWidth={8}
    />
  );
}

export function MonthByYearHeatmap({
  values,
}: {
  values: MonthByYearHeatmapCell[];
}) {
  if (values.length === 0) return null;

  const minYear = Math.min(...values.map((value) => value.year));
  const maxYear = Math.max(...values.map((value) => value.year));
  const columns: HeatmapColumn[] = [];
  for (let year = minYear; year <= maxYear; year++) {
    columns.push({ key: `${year}`, label: `${year}` });
  }

  const heatmapValues = new Map(
    values.map((value) => [
      cellKey(`${value.month}`, `${value.year}`),
      value.stream_count,
    ])
  );

  return (
    <Heatmap
      title="Streams by month and year"
      description="Compare seasonal listening patterns across years."
      rows={months.map((month) => ({ key: `${month.value}`, label: month.label }))}
      columns={columns}
      values={heatmapValues}
      cellHeight={18}
      cellWidth={42}
    />
  );
}

export function HourByWeekdayHeatmap({
  values,
}: {
  values: HourByWeekdayHeatmapCell[];
}) {
  if (values.length === 0) return null;

  const columns = Array.from({ length: 24 }, (_, hour) => ({
    key: `${hour}`,
    label: hour % 3 === 0 ? `${hour}:00` : "",
  }));
  const heatmapValues = new Map(
    values.map((value) => [
      cellKey(`${value.day_of_week}`, `${value.hour}`),
      value.stream_count,
    ])
  );

  return (
    <Heatmap
      title="Streams by weekday and hour"
      description="See when in the week you tend to listen most."
      rows={weekdays.map((day) => ({ key: `${day.value}`, label: day.label }))}
      columns={columns}
      values={heatmapValues}
      cellHeight={14}
      cellWidth={24}
    />
  );
}
