import { FC, useState, useCallback } from "react";
import {
  Container,
  Button,
  Typography,
  Box,
  Divider,
  Stack,
} from "@mui/material";
import { StickyNote } from "@mirohq/websdk-types";

// Miro公式のサポートカラー型
const STICKY_COLORS = [
  "yellow",
  "green",
  "blue",
  "pink",
  "orange",
  "gray",
  "red",
  "violet",
  "light_yellow",
  "light_green",
  "dark_green",
  "cyan",
  "light_pink",
  "light_blue",
  "dark_blue",
  "black",
] as const;
type StickyColor = (typeof STICKY_COLORS)[number];

/**
 * ランダムな文字を取得する
 *
 * @returns {*}
 */
function getRandomChar() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  return chars[Math.floor(Math.random() * chars.length)];
}

/**
 * ランダムな色を取得する
 *
 * @returns {*}
 */
function getRandomColor(): StickyColor {
  return STICKY_COLORS[Math.floor(Math.random() * STICKY_COLORS.length)];
}

// 付箋の専用タグ名
const GRID_TAG_NAME = "speedtest";

/**
 * 付箋の専用タグを取得する
 * なければ作成する
 *
 * @returns {Promise<Tag>}
 */
async function getOrCreateGridTag() {
  const tags = await miro.board.get({ type: "tag" });
  let tag = tags.find((t: any) => t.title === GRID_TAG_NAME);
  if (!tag) {
    tag = await miro.board.createTag({ title: GRID_TAG_NAME, color: "green" });
  }
  return tag;
}

export const TestStickyNote: FC = () => {
  const baseUrl = String(process.env.NEXT_PUBLIC_BACKEND_URL);

  const [timePostSDK, setTimePostSDK] = useState<number | null>(null);
  const [timeGetSDK, setTimeGetSDK] = useState<number | null>(null);
  const [timePutSDK, setTimePutSDK] = useState<number | null>(null);
  const [timeDeleteSDK, setTimeDeleteSDK] = useState<number | null>(null);

  const [timePostAPI, setTimePostAPI] = useState<number | null>(null);
  const [timeGetAPI, setTimeGetAPI] = useState<number | null>(null);
  const [timePutAPI, setTimePutAPI] = useState<number | null>(null);
  const [timeDeleteAPI, setTimeDeleteAPI] = useState<number | null>(null);
  const [createdStickyIds, setCreatedStickyIds] = useState<string[]>([]);
  const [tagId, setTagId] = useState<string>("");

  /**
   * 付箋生成
   *
   * @type {*}
   */
  const postStickyNotesSDK = useCallback(async () => {
    const start = performance.now();
    const startX = 0;
    const startY = 0;
    const offsetX = 200;
    const offsetY = 200;
    const numX = 10;
    const numY = 10;
    const gridTag = await getOrCreateGridTag();

    // 並列実行で付箋を生成する
    const stickyPromises = [];
    for (let i = 0; i < numY; i++) {
      for (let j = 0; j < numX; j++) {
        stickyPromises.push(
          miro.board.createStickyNote({
            content: getRandomChar(),
            x: startX + j * offsetX,
            y: startY + i * offsetY,
            style: { fillColor: getRandomColor() },
            tagIds: [gridTag.id],
          }),
        );
      }
    }
    const stickies = await Promise.all(stickyPromises);

    await miro.board.viewport.zoomTo(stickies);
    setCreatedStickyIds(stickies.map((s: any) => s.id));
    const end = performance.now();
    setTimePostSDK((end - start) / 1000);
  }, []);

  /**
   * 付箋取得
   *
   * @type {*}
   */
  const getStickyNotesSDK = useCallback(async () => {
    if (createdStickyIds.length === 0) return;
    const start = performance.now();
    const contents: string[] = [];
    for (const id of createdStickyIds) {
      const item = await miro.board.getById(id);
      if (item && item.type === "sticky_note") {
        const sticky = item as StickyNote;
        contents.push(sticky.content);
      }
    }
    const end = performance.now();
    setTimeGetSDK((end - start) / 1000);
    // return contents;
    for (const content of contents) {
      console.log(content);
    }
  }, [createdStickyIds]);

  /**
   * 付箋更新
   *
   * @type {*}
   */
  const putStickyNotesSDK = useCallback(async () => {
    console.log("AAAAA");

    if (createdStickyIds.length === 0) return;
    console.log("BBBBB");

    const start = performance.now();
    const stickyPromises = [];
    for (const id of createdStickyIds) {
      const item = await miro.board.getById(id);
      if (item && item.type === "sticky_note") {
        const sticky = item as StickyNote;
        sticky.content = getRandomChar();
        sticky.style.fillColor = getRandomColor();
        console.log(sticky.content);
        stickyPromises.push(sticky.sync());
      }
    }
    await Promise.all(stickyPromises);
    const end = performance.now();
    setTimePutSDK((end - start) / 1000);
  }, [createdStickyIds]);

  /**
   * 付箋削除
   *
   * @type {*}
   */
  const deleteStickyNotesSDK = useCallback(async () => {
    if (createdStickyIds.length === 0) return;
    const start = performance.now();
    const stickyPromises = [];
    for (const id of createdStickyIds) {
      const sticky = await miro.board.getById(id);
      if (sticky) {
        stickyPromises.push(miro.board.remove(sticky));
      }
    }
    await Promise.all(stickyPromises);

    setCreatedStickyIds([]);
    const end = performance.now();
    setTimeDeleteSDK((end - start) / 1000);
  }, [createdStickyIds]);

  /**
   * 付箋生成API
   *
   * @type {*}
   */
  const postStickyNotesAPI = useCallback(async () => {
    const timeStart = performance.now();

    console.log("createStickyNotesByAPI");

    const response = await fetch(`${baseUrl}/api/miro/sticky_note/post`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: (await miro.board.getUserInfo()).id,
        board_id: (await miro.board.getInfo()).id,
      }),
    });

    const timeEnd = performance.now();

    setTagId((await response.json()).tag_id);
    setTimePostAPI((timeEnd - timeStart) / 1000);
  }, []);

  const getStickyNotesAPI = useCallback(async () => {
    const timeStart = performance.now();

    console.log("getStickyNotesByAPI");

    await fetch(`${baseUrl}/api/miro/sticky_note/get`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: (await miro.board.getUserInfo()).id,
        board_id: (await miro.board.getInfo()).id,
      }),
    });

    const timeEnd = performance.now();
    setTimeGetAPI((timeEnd - timeStart) / 1000);
  }, []);

  const putStickyNotesAPI = useCallback(async () => {
    const timeStart = performance.now();

    console.log("putStickyNotesByAPI");

    await fetch(`${baseUrl}/api/miro/sticky_note/put`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: (await miro.board.getUserInfo()).id,
        board_id: (await miro.board.getInfo()).id,
      }),
    });

    const timeEnd = performance.now();
    setTimePutAPI((timeEnd - timeStart) / 1000);
  }, []);

  const deleteStickyNotesAPI = useCallback(async () => {
    const timeStart = performance.now();

    console.log("deleteStickyNotesByAPI");

    await fetch(`${baseUrl}/api/miro/sticky_note/delete`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: (await miro.board.getUserInfo()).id,
        board_id: (await miro.board.getInfo()).id,
      }),
    });

    const timeEnd = performance.now();
    setTimeDeleteAPI((timeEnd - timeStart) / 1000);
  }, []);

  return (
    <Container
      maxWidth="sm"
      sx={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        padding: 0,
        overflow: "auto",
        alignItems: "center",
      }}
    >
      <Typography variant="h4" gutterBottom style={{ marginTop: 8 }}>
        Sticky Note (10x10)
      </Typography>
      <Divider />
      <Container
        sx={{
          display: "flex",
          flexDirection: "column",
          padding: 0,
          alignItems: "center",
        }}
      >
        <Typography variant="h6" gutterBottom>
          Miro WEB SDK
        </Typography>
        <Box sx={{ gap: 2, display: "flex", flexDirection: "row" }}>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={postStickyNotesSDK}
            >
              生成
            </Button>
            {timePostSDK !== null && (
              <span style={{ marginLeft: 16 }}>
                {timePostSDK.toFixed(2)} 秒
              </span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={getStickyNotesSDK}
            >
              取得
            </Button>
            {timeGetSDK !== null && (
              <span style={{ marginLeft: 16 }}>{timeGetSDK.toFixed(2)} 秒</span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={putStickyNotesSDK}
            >
              更新
            </Button>
            {timePutSDK !== null && (
              <span style={{ marginLeft: 16 }}>{timePutSDK.toFixed(2)} 秒</span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={deleteStickyNotesSDK}
            >
              削除
            </Button>
            {timeDeleteSDK !== null && (
              <span style={{ marginLeft: 16 }}>
                {timeDeleteSDK.toFixed(2)} 秒
              </span>
            )}
          </Stack>
        </Box>
      </Container>
      <Divider />
      <Container
        sx={{
          display: "flex",
          flexDirection: "column",
          padding: 0,
          alignItems: "center",
          mt: 4,
        }}
      >
        <Typography variant="h6" gutterBottom>
          Miro REST API
        </Typography>
        <Box sx={{ gap: 2, display: "flex", flexDirection: "row" }}>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={postStickyNotesAPI}
            >
              生成
            </Button>
            {timePostAPI !== null && (
              <span style={{ marginLeft: 16 }}>
                {timePostAPI.toFixed(2)} 秒
              </span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={getStickyNotesAPI}
            >
              取得
            </Button>
            {timeGetAPI !== null && (
              <span style={{ marginLeft: 16 }}>{timeGetAPI.toFixed(2)} 秒</span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={putStickyNotesAPI}
            >
              更新
            </Button>
            {timePutAPI !== null && (
              <span style={{ marginLeft: 16 }}>{timePutAPI.toFixed(2)} 秒</span>
            )}
          </Stack>
          <Stack>
            <Button
              variant="contained"
              color="primary"
              onClick={deleteStickyNotesAPI}
            >
              削除
            </Button>
            {timeDeleteAPI !== null && (
              <span style={{ marginLeft: 16 }}>
                {timeDeleteAPI.toFixed(2)} 秒
              </span>
            )}
          </Stack>
        </Box>
      </Container>
    </Container>
  );
};
