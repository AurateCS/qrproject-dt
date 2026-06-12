CREATE TABLE IF NOT EXISTS phanquyen (
    "TK"         VARCHAR   NOT NULL,
    "controller" VARCHAR   NOT NULL,
    "access_yn"  SMALLINT  NOT NULL DEFAULT 0,
    "new_yn"     SMALLINT  NOT NULL DEFAULT 0,
    "edit_yn"    SMALLINT  NOT NULL DEFAULT 0,
    "delete_yn"  SMALLINT  NOT NULL DEFAULT 0,
    PRIMARY KEY ("TK", "controller")
);
