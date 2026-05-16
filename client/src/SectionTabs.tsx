import {
  IconDisc,
  IconInfoCircle,
  IconList,
  IconMicrophone2,
  IconMusic,
  IconStar,
  IconTag,
  IconCalendar,
  IconUsers,
  IconThumbUp,
} from "@tabler/icons-react";
import { ReactNode, useEffect, useState } from "react";

import { ActiveFilters } from "./api";
import styles from "./SectionTabs.module.css";
import { useArtists } from "./useApi";
import { useFilters } from "./useFilters";

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
    f.wrapped ||
    f.tracks?.length === 1 ||
    f.artists?.length === 1 ||
    f.albums?.length === 1 ||
    f.playlists?.length === 1 ||
    f.producers?.length === 1 ||
    f.labels?.length === 1 ||
    f.genres?.length === 1 ||
    f.years?.length === 1
  );
}

export function useSectionDefs(sectionContent: Record<string, ReactNode>): SectionDef[] {
  const { total: artistCount } = useArtists({ sort: "Most streams", limit: 1 });

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
      hidden: () => false,
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
      hidden: () => false,
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
      hidden: () => false,
      content: sectionContent.years,
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
  const [activeId, setActiveId] = useState<string | null>(null);

  // Auto-select the Details tab when it appears
  const detailsVisible = visibleSections.some((s) => s.id === "details");
  useEffect(() => {
    if (detailsVisible) {
      setActiveId("details");
    } else if (activeId === "details") {
      setActiveId(null);
    }
  }, [detailsVisible]);

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
            onClick={() => setActiveId(section.id)}
          >
            {section.icon}
            <span className={styles.tabLabel}>{section.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
