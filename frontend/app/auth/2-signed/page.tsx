"use client";
import { Typography, Container, CircularProgress } from "@mui/material";
import { useEffect } from "react";
import congraturations from "@/public/congratulations.png";
import Image from "next/image";

export default function Signed() {
  useEffect(() => {
    const fetchAuthUrl = async () => {
      // 認証後、3秒待機した後、モーダルを閉じる
      const timeoutId = setTimeout(() => {
        (async () => {
          await miro.board.ui.closeModal();
        })();
      }, 3000);
    };
    fetchAuthUrl();
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
        justifyContent: "center",
      }}
    >
      <Image
        src={congraturations}
        alt="Congratulations"
        width={200}
        height={200}
        style={{ marginBottom: "20px" }}
      />
      <Typography variant="h4" gutterBottom>
        Completed to install
      </Typography>
      <CircularProgress />
    </Container>
  );
}
