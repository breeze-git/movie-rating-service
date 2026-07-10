-- TABLE movies --

CREATE TABLE public.movies (
	id uuid NOT NULL,
	director_id uuid NOT NULL,
	title varchar(50) NOT NULL,
	description text NOT NULL,
	release_year int4 NOT NULL,
	CONSTRAINT check_release_year CHECK (((release_year >= 1895) AND ((release_year)::numeric <= EXTRACT(year FROM now())))),
	CONSTRAINT movies_pkey PRIMARY KEY (id),
	CONSTRAINT movies_director_id_fkey FOREIGN KEY (director_id) REFERENCES public.directors(id) ON DELETE CASCADE
);
CREATE INDEX ix_movies_director_id ON public.movies USING btree (director_id);
CREATE INDEX ix_movies_release_year ON public.movies USING btree (release_year);

-- TABLE directors --

CREATE TABLE public.directors (
	id uuid NOT NULL,
	first_name varchar(50) NOT NULL,
	last_name varchar(50) NOT NULL,
	CONSTRAINT directors_pkey PRIMARY KEY (id)
);

-- TABLE countries --

CREATE TABLE public.countries (
	id serial4 NOT NULL,
	"name" varchar(30) NOT NULL,
	CONSTRAINT countries_name_key UNIQUE (name),
	CONSTRAINT countries_pkey PRIMARY KEY (id)
);

-- TABLE genres --

CREATE TABLE public.genres (
	id serial4 NOT NULL,
	"name" varchar(30) NOT NULL,
	CONSTRAINT genres_name_key UNIQUE (name),
	CONSTRAINT genres_pkey PRIMARY KEY (id)
);

-- TABLE users --

CREATE TABLE public.users (
	id uuid NOT NULL,
	username varchar(50) NOT NULL,
	first_name varchar(50) NULL,
	last_name varchar(50) NULL,
	email varchar(100) NOT NULL,
	hashed_password varchar(60) NOT NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_username_key UNIQUE (username)
);

-- TABLE roles --

CREATE TABLE public.roles (
	id serial4 NOT NULL,
	"name" varchar(50) NOT NULL,
	CONSTRAINT roles_name_key UNIQUE (name),
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

-- TABLE permissions --

CREATE TABLE public.permissions (
	id serial4 NOT NULL,
	"name" varchar(50) NOT NULL,
	CONSTRAINT permissions_name_key UNIQUE (name),
	CONSTRAINT permissions_pkey PRIMARY KEY (id)
);

-- TABLE reviews --

CREATE TABLE public.reviews (
	id uuid NOT NULL,
	user_id uuid NOT NULL,
	message text NOT NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	updated_at timestamptz NULL,
	movie_id uuid NOT NULL,
	rating int4 NULL,
	CONSTRAINT reviews_pkey PRIMARY KEY (id),
	CONSTRAINT reviews_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE,
	CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX ix_reviews_created_at ON public.reviews USING btree (created_at);
CREATE INDEX ix_reviews_movie_id ON public.reviews USING btree (movie_id);
CREATE INDEX ix_reviews_user_id ON public.reviews USING btree (user_id);

-- TABLE country_movies --

CREATE TABLE public.country_movies (
	movie_id uuid NOT NULL,
	country_id int4 NOT NULL,
	CONSTRAINT country_movies_pkey PRIMARY KEY (movie_id, country_id),
	CONSTRAINT country_movies_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE,
	CONSTRAINT country_movies_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE
);
CREATE INDEX ix_country_movies_country_id ON public.country_movies USING btree (country_id);

-- TABLE genre_movies --

CREATE TABLE public.genre_movies (
	movie_id uuid NOT NULL,
	genre_id int4 NOT NULL,
	CONSTRAINT genre_movies_pkey PRIMARY KEY (movie_id, genre_id),
	CONSTRAINT genre_movies_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE CASCADE,
	CONSTRAINT genre_movies_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE
);
CREATE INDEX ix_genre_movies_genre_id ON public.genre_movies USING btree (genre_id);

-- TABLE user_roles --

CREATE TABLE public.user_roles (
	user_id uuid NOT NULL,
	role_id int4 NOT NULL,
	CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id),
	CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE,
	CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX ix_user_roles_role_id ON public.user_roles USING btree (role_id);

-- TABLE role_permissions --

CREATE TABLE public.role_permissions (
	role_id int4 NOT NULL,
	permission_id int4 NOT NULL,
	CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id),
	CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE,
	CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE
);
CREATE INDEX ix_role_permissions_permission_id ON public.role_permissions USING btree (permission_id);

-- CREATING DEFAULT ROLES AND PERMISSIONS --

INSERT INTO public.roles(name) VALUES ('admin'), ('user');

INSERT INTO public.permissions(name) 
VALUES ('reviews:read'), ('reviews:create'), 
	   ('reviews:manage'), ('reviews:delete');

INSERT INTO public.role_permissions (role_id, permission_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:read')),
  ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:create'));
   
