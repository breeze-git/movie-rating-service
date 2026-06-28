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

-- TABLE user_roles --

CREATE TABLE public.user_roles (
	user_id uuid NOT NULL,
	role_id int4 NOT NULL,
	CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id),
	CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE,
	CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX user_roles_role_id ON public.user_roles USING btree (role_id);

-- TABLE permissions --

CREATE TABLE public.permissions (
	id serial4 NOT NULL,
	"name" varchar(50) NOT NULL,
	CONSTRAINT permissions_name_key UNIQUE (name),
	CONSTRAINT permissions_pkey PRIMARY KEY (id)
);

-- TABLE role_permissions --

CREATE TABLE public.role_permissions (
	role_id int4 NOT NULL,
	permission_id int4 NOT NULL,
	CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id),
	CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE,
	CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE
);
CREATE INDEX role_permissions_permission_id ON public.role_permissions USING btree (permission_id);

-- TABLE reviews --

CREATE TABLE public.reviews (
	id uuid NOT NULL,
	user_id uuid NOT NULL,
	message text NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NULL,
	CONSTRAINT reviews_pkey PRIMARY KEY (id),
	CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX reviews_created_at ON public.reviews USING btree (created_at);
CREATE INDEX reviews_user_id ON public.reviews USING btree (user_id);

-- CREATING DEFAULT ROLES AND PERMISSIONS --

INSERT INTO public.roles(name) VALUES ('admin'), ('user');

INSERT INTO public.permissions(name) 
VALUES ('reviews:read'), ('reviews:create'), 
	   ('reviews:manage'), ('reviews:delete');

INSERT INTO public.role_permissions (role_id, permission_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:read')),
  ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'reviews:create'));
   
