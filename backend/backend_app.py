from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"post_id": 1, "title": "First post", "content": "This is the first post."},
    {"post_id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """Get all posts or create a new post. If the request method is GET: Return all posts in their original
     order or sorted based on provided parameters.
     If the request method is POST: Create a new post with the provided JSON data.
     Returns JSON response containing the list of posts or the newly created post."""
    if request.method == 'POST':
        new_post = request.get_json()
        if not validate_post_data(new_post):
            return jsonify({"error": "Invalid post data - either 'title' or 'content' is missing."}), 400

        existing_post = find_existing_post(new_post)
        if existing_post:
            return jsonify({"error": "Post already exists"}), 409

        new_id = max(post['post_id'] for post in POSTS) + 1
        new_post['post_id'] = new_id

        POSTS.append(new_post)
        return jsonify(new_post), 201

    else:
        # Handle GET request to list posts
        sort_field = request.args.get('sort')
        sort_direction = request.args.get('direction')

        if sort_field and not is_valid_sort_field(sort_field):
            return jsonify({"error": f"Invalid sort field: {sort_field}"}), 400

        if sort_direction and not is_valid_sort_direction(sort_direction):
            return jsonify({"error": f"Invalid sort direction: {sort_direction}"}), 400

        sorted_posts = sort_posts(sort_field, sort_direction)

        return jsonify(sorted_posts)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Post_id to be deleted is the parameter, and the post is deleted. If no post is found an error message is returned
    """
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a post with the given post_id.The post_id of the post to be updated is the parameter.
    Returns: JSON response saying post updated, and error 404 message post not found otherwise"""
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json()
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']

    return jsonify({"message": f"Post with id {post_id} has been updated successfully."}), 200


@app.route('/api/posts/search', methods=['GET'])
def post_search():
    """Search for posts based on provided search terms. Returns JSON response containing the filtered
     list of posts based on the provided search terms."""
    post_id = request.args.get('post_id')
    content = request.args.get('content')
    title = request.args.get('title')
    filtered_posts = []

    if post_id:
        post = find_post_by_id(int(post_id))
        if post:
            filtered_posts.append(post)
    else:
        if content:
            filtered_posts = [post for post in POSTS if content in post.get('content', '')]
        if title:
            filtered_posts = [post for post in POSTS if title in post.get('title', '')]

    return jsonify(filtered_posts)


def validate_post_data(data):
    """ Validate the required fields of a new post. Takes the JSON data of the new post as parameter.
    Returns True if the required fields are present, False otherwise."""
    if "title" not in data or "content" not in data:
        return False
    return True


def find_existing_post(post):
    """ Find if a post with the same title and content already exists and returns it. None otherwise """
    for existing_post in POSTS:
        if existing_post['title'] == post['title'] and existing_post['content'] == post['content']:
            return existing_post
    return None


def find_post_by_id(post_id):
    """Finds and returns the post with the id `post_id`.
    If there is no post with this id, return None."""
    for post in POSTS:
        try:
            if post['post_id'] == post_id:
                return post
        except KeyError:
            pass
    return None


def is_valid_sort_field(field):
    """ Checks if the provided sort field is valid. Returns True if the sort field is valid, False otherwise."""
    valid_sort_fields = ['title', 'content']
    return field in valid_sort_fields


def is_valid_sort_direction(direction):
    """ Check if the provided sort direction is valid. Returns True if the sort direction is valid, False otherwise."""
    valid_sort_directions = ['asc', 'desc']
    return direction in valid_sort_directions


def sort_posts(field, direction):
    """Sort the posts based on the provided field (title or content) and direction (ascending or descending).
    Returns: The sorted list of posts."""
    if field == 'title':
        sorted_posts = sorted(POSTS, key=lambda post: post['title'])
    elif field == 'content':
        sorted_posts = sorted(POSTS, key=lambda post: post['content'])
    else:
        return POSTS

    if direction == 'desc':
        sorted_posts.reverse()

    return sorted_posts


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
