"use client";
import {
  Box,
  Button,
  Container,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { useEffect, useState } from "react";
import PersonIcon from "@mui/icons-material/Person";
import DashboardIcon from "@mui/icons-material/Dashboard";
import LightbulbIcon from "@mui/icons-material/Lightbulb";

export default function Signin() {
  const baseUrl = String(process.env.NEXT_PUBLIC_BACKEND_URL);
  const [userId, setUserId] = useState<string | null>(null);
  const [boardId, setBoardId] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<boolean | null>(null);

  const fetchMiroIds = async () => {
    // userId, boardIdをSDK経由で取得
    const nowUserId = (await miro.board.getUserInfo()).id;
    const nowBoardId = (await miro.board.getInfo()).id;
    if (nowBoardId === null || nowUserId === null) {
      console.error("Failed to get userId or boardId");
      return;
    }
    setUserId(nowUserId);
    setBoardId(nowBoardId);
  };

  const fetchAuthStatus = async () => {
    // 認証ステータスをフェッチ
    console.log("BuserId", userId);

    const authStatusUrl = `${baseUrl}/api/oauth/status?user_id=${encodeURIComponent(String(userId))}`;
    console.log(`app/auth/1-signin/page.tsx ${authStatusUrl}`);
    const authStatusResponse = await fetch(authStatusUrl, {
      method: "GET",
      credentials: "include",
    });
    // 認証ステータスを取得
    const authStatusBody = await authStatusResponse.json();
    setAuthStatus(authStatusBody.status);
    if (!authStatusResponse.ok) {
      console.error(
        "Failed to fetch the auth status.:",
        authStatusResponse.status,
      );
      return;
    }
  };

  useEffect(() => {
    void fetchMiroIds();
  }, []);

  useEffect(() => {
    if (userId) {
      void fetchAuthStatus();
    }
  }, [userId]);

  useEffect(() => {
    // 認証済みなら、トップ画面へ遷移
    if (authStatus === true) {
      window.location.href = "/";
    }
  }, [authStatus]);

  const handleClick = async () => {
    // 認証済みなら、トップ画面へ遷移
    if (authStatus === true) {
      window.location.href = "/";
    }

    // 認証URLをバックエンドから取得
    const authRequestUrl = `${baseUrl}/api/oauth/authorize?user_id=${userId}`;
    const authRequestResponse = await fetch(authRequestUrl, {
      method: "POST",
      credentials: "include",
    });
    if (!authRequestResponse.ok) {
      console.error(
        "Failed to fetch the auth request URL:",
        authRequestResponse.status,
      );
      return;
    }
    // 認証URLをバックエンドから取得
    const authRedirectUrl = (await authRequestResponse.json()).url;
    console.log("認証URL: ", authRedirectUrl);

    // 認証URLをMiroモーダルで開く
    const modal = await miro.board.ui.openModal({
      url: authRedirectUrl,
      width: 800,
      height: 600,
    });
    await modal.waitForClose().then(async () => {
      console.log("モーダルが閉じました");
      await fetchAuthStatus();
    });
  };

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
        justifyContent: "center",
      }}
    >
      <Typography variant="h4" gutterBottom>
        認証が必要です
      </Typography>
      <Typography variant="body1" gutterBottom>
        このアプリを使用するには、認証が必要です。
      </Typography>
      <Typography variant="body2" gutterBottom>
        認証を行うには、下のボタンをクリックしてください。
      </Typography>
      <Box gap={4} display="flex">
        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
          onClick={handleClick}
        >
          Miro 認証
        </Button>
      </Box>
      <List sx={{ mt: 8 }}>
        <ListItem>
          <ListItemIcon>
            <PersonIcon />
          </ListItemIcon>
          <ListItemText primary={`User ID: ${userId}`} />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary={`Board ID: ${boardId}`} />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <LightbulbIcon />
          </ListItemIcon>
          <ListItemText primary={`Auth Status: ${authStatus}`} />
        </ListItem>
      </List>
    </Container>
  );
}
