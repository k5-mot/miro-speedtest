import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

// Cookieユーティリティ
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() || null;
  return null;
}

function setCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; expires=${expires}; SameSite=Lax; Secure`;
}

// 型定義
export type TokenContextType = {
  code: string;
  state: string;
  clientId: string;
  teamId: string;
  setCode: (code: string) => void;
  setState: (state: string) => void;
  setClientId: (clientId: string) => void;
  setTeamId: (teamId: string) => void;
};

const TokenContext = createContext<TokenContextType | undefined>(undefined);

export const TokenProvider = ({ children }: { children: ReactNode }) => {
  const [code, setCode] = useState<string>("");
  const [state, setState] = useState<string>("");
  const [clientId, setClientId] = useState<string>("");
  const [teamId, setTeamId] = useState<string>("");

  // Cookieから初期化
  useEffect(() => {
    setCode(getCookie("code") || "");
    setState(getCookie("state") || "");
    setClientId(getCookie("client_id") || "");
    setTeamId(getCookie("team_id") || "");
  }, []);

  // Cookieも更新
  const updateCode = (val: string) => {
    setCode(val);
    setCookie("code", val);
  };
  const updateState = (val: string) => {
    setState(val);
    setCookie("state", val);
  };
  const updateClientId = (val: string) => {
    setClientId(val);
    setCookie("client_id", val);
  };
  const updateTeamId = (val: string) => {
    setTeamId(val);
    setCookie("team_id", val);
  };

  return (
    <TokenContext.Provider
      value={{
        code,
        state,
        clientId,
        teamId,
        setCode: updateCode,
        setState: updateState,
        setClientId: updateClientId,
        setTeamId: updateTeamId,
      }}
    >
      {children}
    </TokenContext.Provider>
  );
};

export function useToken() {
  const ctx = useContext(TokenContext);
  if (!ctx) throw new Error("useToken must be used within a TokenProvider");
  return ctx;
}
