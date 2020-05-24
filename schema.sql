
CREATE TABLE comics (
       id SERIAL PRIMARY KEY,
       nickname VARCHAR(32) NOT NULL UNIQUE,
       name TEXT NOT NULL UNIQUE
 );

CREATE TABLE archive (
       id SERIAL PRIMARY KEY,
       comicid INTEGER REFERENCES comics(id),
       tag INTEGER NOT NULL UNIQUE,
       nexttag INTEGER REFERENCES archive(tag),
       prevtag INTEGER REFERENCES archive(tag),
       url TEXT NOT NULL,
       parsed_at TIMESTAMP,
       UNIQUE(comicid, tag)
);

CREATE INDEX archive_tag_index ON archive (comicid, tag);
CREATE INDEX archive_history_index ON archive (comicid, parsed_at);

CREATE TABLE images (
       id SERIAL PRIMARY KEY,
       archiveid INTEGER REFERENCES archive(id),
       image_path text NOT NULL,
       width SMALLINT NOT NULL,
       height SMALLINT NOT NULL,
       original_filename text
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

-- Data


INSERT INTO comics (nickname, name) VALUES ('sluggy', 'Sluggy Freelance');
INSERT INTO comics (nickname, name) VALUES ('userfriendly', 'User Friendly');
INSERT INTO comics (nickname, name) VALUES ('schlock', 'Schlock Mercenary');
INSERT INTO comics (nickname, name) VALUES ('reallife', 'Real Life Comics');
INSERT INTO comics (nickname, name) VALUES ('eightbit', '8-Bit Theater');
