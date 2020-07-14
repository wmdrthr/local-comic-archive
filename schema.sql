
CREATE TABLE comics (
       id SERIAL PRIMARY KEY,
       nickname VARCHAR(32) NOT NULL UNIQUE,
       name TEXT NOT NULL UNIQUE
 );

CREATE TABLE archive (
       id SERIAL PRIMARY KEY,
       comicid INTEGER REFERENCES comics(id),
       tag INTEGER NOT NULL,
       nexttag INTEGER REFERENCES archive(tag),
       prevtag INTEGER REFERENCES archive(tag),
       slug VARCHAR(32),
       url TEXT NOT NULL,
       parsed_at TIMESTAMP
);

CREATE UNIQUE INDEX archive_tag_index ON archive (comicid, tag);
CREATE UNIQUE INDEX archive_slug_index ON archive (comicid, slug);
CREATE INDEX archive_history_index ON archive (comicid, parsed_at);

CREATE TABLE images (
       id SERIAL PRIMARY KEY,
       archiveid INTEGER REFERENCES archive(id),
       image_path TEXT NOT NULL,
       width SMALLINT NOT NULL,
       height SMALLINT NOT NULL,
       imagetype SMALLINT DEFAULT 1,
       caption TEXT,
       original_filename TEXT
);

CREATE INDEX images_archiveid_index ON images (archiveid);

CREATE TABLE titles (
       id SERIAL PRIMARY KEY,
       archiveid INTEGER REFERENCES archive(id),
       title TEXT NOT NULL
);

CREATE INDEX titles_archiveid_index ON titles (archiveid);

CREATE TABLE annotations (
       id SERIAL PRIMARY KEY,
       archiveid INTEGER REFERENCES archive(id),
       annotation TEXT NOT NULL
);

CREATE INDEX annotations_archiveid_index ON annotations (archiveid);
