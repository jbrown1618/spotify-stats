import {
  IconCalendar,
  IconChartBar,
  IconDisc,
  IconInfoCircle,
  IconList,
  IconMicrophone2,
  IconMusic,
  IconStar,
  IconTag,
  IconThumbUp,
  IconUsers,
} from "@tabler/icons-react";
import { ReactNode, useEffect, useState } from "react";

import { ActiveFilters } from "./api";
import styles from "./SectionTabs.module.css";
import { useAlbums, useArtists, useReleaseYears } from "./useApi";
import { useFilters } from "./useFilters";

const SECTION_QUERY_PARAM = "section";

interface SectionDef {
  id: string;
  label: string;
  icon: ReactNode;
  hidden: (filters: ActiveFilters) => boolean;
  content: ReactNode;
}

interface SectionTabsProps {
  sections: SectionDef[];
}

function hasDetails(f: ActiveFilters): boolean {
  return !!(
    f.tracks?.length === 1 ||
    f.artists?.length === 1 ||
    f.producers?.length === 1
  );
}

export function useSectionDefs(sectionContent: Record<string, ReactNode>): SectionDef[] {
  const { total: artistCount } = useArtists({ sort: "Most streams", limit: 1 });
  const { total: albumCount } = useAlbums({ sort: "Most streams", limit: 1 });
  const { total: yearCount } = useReleaseYears({ sort: "Newest", limit: 1 });

  return [
    {
      id: "details",
      label: "Details",
      icon: <IconInfoCircle size={20} />,
      hidden: (f) => !hasDetails(f),
      content: sectionContent.details,
    },
    {
      id: "tracks",
      label: "Tracks",
      icon: <IconMusic size={20} />,
      hidden: (f) => f.tracks?.length === 1,
      content: sectionContent.tracks,
    },
    {
      id: "artists",
      label: "Artists",
      icon: <IconMicrophone2 size={20} />,
      hidden: (f) => f.artists?.length === 1 || artistCount <= 1,
      content: sectionContent.artists,
    },
    {
      id: "albums",
      label: "Albums",
      icon: <IconDisc size={20} />,
      hidden: (f) => f.albums?.length === 1 || f.tracks?.length === 1 || albumCount <= 1,
      content: sectionContent.albums,
    },
    {
      id: "playlists",
      label: "Playlists",
      icon: <IconList size={20} />,
      hidden: () => false,
      content: sectionContent.playlists,
    },
    {
      id: "labels",
      label: "Labels",
      icon: <IconTag size={20} />,
      hidden: () => false,
      content: sectionContent.labels,
    },
    {
      id: "genres",
      label: "Genres",
      icon: <IconStar size={20} />,
      hidden: () => false,
      content: sectionContent.genres,
    },
    {
      id: "producers",
      label: "Producers",
      icon: <IconUsers size={20} />,
      hidden: () => false,
      content: sectionContent.producers,
    },
    {
      id: "years",
      label: "Years",
      icon: <IconCalendar size={20} />,
      hidden: () => yearCount <= 1,
      content: sectionContent.years,
    },
    {
      id: "insights",
      label: "Insights",
      icon: <IconChartBar size={20} />,
      hidden: () => false,
      content: sectionContent.insights,
    },
    {
      id: "recommendations",
      label: "For You",
      icon: <IconThumbUp size={20} />,
      hidden: () => false,
      content: sectionContent.recommendations,
    },
  ];
}

export function SectionTabs({ sections }: SectionTabsProps) {
  const filters = useFilters();
  const visibleSections = sections.filter((s) => !s.hidden(filters));
  const [activeId, setActiveId] = useState<string | null>(() =>
    new URLSearchParams(window.location.search).get(SECTION_QUERY_PARAM)
  );

  useEffect(() => {
    const onBackOrForward = () => {
      setActiveId(
        new URLSearchParams(window.location.search).get(SECTION_QUERY_PARAM)
      );
    };

    window.addEventListener("popstate", onBackOrForward);
    return () => window.removeEventListener("popstate", onBackOrForward);
  }, []);

  // Filter navigation removes the section parameter and selects the first
  // available section, which is Details when a detail view is present.
  useEffect(() => {
    setActiveId(
      new URLSearchParams(window.location.search).get(SECTION_QUERY_PARAM)
    );
  }, [filters]);

  const resolvedActiveId =
    activeId && visibleSections.some((s) => s.id === activeId)
      ? activeId
      : visibleSections[0]?.id ?? null;

  const activeSection = visibleSections.find((s) => s.id === resolvedActiveId);

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        {activeSection?.content}
      </div>
      <nav className={styles.tabBar}>
        {visibleSections.map((section) => (
          <button
            key={section.id}
            className={`${styles.tab} ${section.id === resolvedActiveId ? styles.tabActive : ""}`}
            onClick={() => {
              window.scrollTo({ top: 0 });
              if (section.id === resolvedActiveId) return;

              const url = new URL(window.location.href);
              url.searchParams.set(SECTION_QUERY_PARAM, section.id);
              history.pushState(history.state, "", url);
              setActiveId(section.id);
            }}
          >
            {section.icon}
            <span className={styles.tabLabel}>{section.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
