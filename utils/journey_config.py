import re
from typing import Dict, List, Tuple, Pattern

class JourneyActionMapper:

    def __init__(self):
        """
        Initialize patterns for matching URLs to actions.
        Format: (compiled_regex_pattern, {http_method: action_name_template})
        Use {resource}, {parent}, and {id} as placeholders in action names.
        """
        self.patterns: List[Tuple[Pattern, Dict[str, str]]] = [
            # Auth patterns - specific routes
            (re.compile(r'^/api/auth/login/?$'), {
                'POST': 'login',
            }),
            (re.compile(r'^/api/auth/logout/?$'), {
                'POST': 'logout',
            }),
            (re.compile(r'^/api/auth/register/?$'), {
                'POST': 'register',
            }),
            
            # Generic CRUD patterns for single resource collection
            # e.g., /api/posts, /api/events, /api/users
            (re.compile(r'^/api/(\w+)/?$'), {
                'GET': 'list_{resource}',
                'POST': 'create_{resource}',
            }),
            
            # Generic CRUD patterns for single resource item
            # e.g., /api/posts/123, /api/events/456
            (re.compile(r'^/api/(\w+)/(\d+)/?$'), {
                'GET': 'view_{resource}',
                'PUT': 'update_{resource}',
                'PATCH': 'update_{resource}',
                'DELETE': 'delete_{resource}',
            }),
            
            # Nested resource collection patterns
            # e.g., /api/posts/123/comments, /api/events/456/users
            (re.compile(r'^/api/(\w+)/(\d+)/(\w+)/?$'), {
                'GET': 'list_{parent}_{resource}',
                'POST': 'create_{parent}_{resource}',
            }),
            
            # Nested resource item patterns
            # e.g., /api/posts/123/comments/456
            (re.compile(r'^/api/(\w+)/(\d+)/(\w+)/(\d+)/?$'), {
                'GET': 'view_{parent}_{resource}',
                'PUT': 'update_{parent}_{resource}',
                'PATCH': 'update_{parent}_{resource}',
                'DELETE': 'delete_{parent}_{resource}',
            }),
            
            # Special action patterns
            # e.g., /api/events/123/register, /api/posts/456/upvote
            (re.compile(r'^/api/(\w+)/(\d+)/(\w+)/?$'), {
                'POST': '{action}_{resource}',
            }),
        ]
    
    def get_action(self, path: str, method: str) -> str:
        """
        Determine action from path and method using pattern matching.
        
        Args:
            path: The request path (e.g., "/api/posts/123")
            method: The HTTP method (e.g., "GET", "POST")
        
        Returns:
            A descriptive action name (e.g., "view_post", "create_comment")
        """
        for pattern, method_actions in self.patterns:
            match = pattern.match(path)
            if match and method in method_actions:
                action_template = method_actions[method]
                
                # Extract captured groups from the regex
                groups = match.groups()
                
                # Replace {resource} placeholder
                if '{resource}' in action_template:
                    if len(groups) >= 1:
                        # Find the resource name (last alphabetic group)
                        resource = None
                        for group in reversed(groups):
                            if group and group.isalpha():
                                resource = self._singularize(group)
                                break
                        
                        if resource:
                            action_template = action_template.replace('{resource}', resource)
                
                # Replace {parent} placeholder
                if '{parent}' in action_template and len(groups) >= 3:
                    parent = self._singularize(groups[0])
                    action_template = action_template.replace('{parent}', parent)
                
                # Replace {action} placeholder (for special actions like register, upvote)
                if '{action}' in action_template and len(groups) >= 3:
                    action_name = groups[2]  # The action part of the URL
                    action_template = action_template.replace('{action}', action_name)
                
                return action_template
        
        # Fallback if no pattern matches
        return self._create_fallback_action(path, method)
    
    def _singularize(self, word: str) -> str:
        if not word:
            return word
        
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('ves'):
            return word[:-3] + 'fe'
        elif word.endswith('ses'):
            return word[:-2]
        elif word.endswith('es'):
            return word[:-2]
        elif word.endswith('s'):
            return word[:-1]
        
        return word
    
    def _create_fallback_action(self, path: str, method: str) -> str:
        """
        Create a generic action name when no pattern matches.
        This is the last resort for creating readable action names.
        """
        clean_path = path.replace("/api/", "").strip("/")
        parts = []
        for part in clean_path.split("/"):
            if not part.isdigit():
                parts.append(part)
        
        if parts:
            return f"{method.lower()}_{'_'.join(parts)}"
        else:
            return method.lower()


# Singleton instance - used by middleware
action_mapper = JourneyActionMapper()